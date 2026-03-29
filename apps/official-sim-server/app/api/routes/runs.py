from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.run_repo import RunRepository
from app.models.models import RunStatus

router = APIRouter()


class RunCreateRequest(BaseModel):
    platform: str = Field(..., description="Platform: taobao, douyin_shop, wecom_kf, jd, xhs, kuaishou")
    scenario_name: str = Field(..., min_length=1, description="Scenario template name")
    strict_mode: bool = Field(default=True, description="Enable strict state machine validation")
    push_enabled: bool = Field(default=True, description="Enable push event generation")
    account_code: Optional[str] = Field(default=None, description="Platform account code")
    seed: Optional[str] = Field(default=None, description="Random seed for deterministic execution")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class RunCreateResponse(BaseModel):
    run_id: str
    run_code: str
    platform: str
    scenario_name: str
    status: str
    current_step: int
    created_at: datetime


class RunGetResponse(BaseModel):
    run_id: str
    run_code: str
    platform: str
    status: str
    current_step: int
    strict_mode: bool
    push_enabled: bool
    seed: Optional[str]
    metadata: Dict[str, Any]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class RunAdvanceRequest(BaseModel):
    next_step: Optional[int] = Field(default=None, description="Optional explicit next step number")


class RunAdvanceResponse(BaseModel):
    run_id: str
    run_code: str
    previous_step: int
    current_step: int
    status: str
    message: str


@router.post("", response_model=RunCreateResponse, status_code=201)
async def create_run(
    request: RunCreateRequest,
    db: Session = Depends(get_db),
):
    repo = RunRepository(db)
    run_code = f"run_{uuid.uuid4().hex[:8]}"

    run = repo.create(
        platform=request.platform,
        run_code=run_code,
        strict_mode=request.strict_mode,
        push_enabled=request.push_enabled,
        seed=request.seed,
        metadata=request.metadata,
    )

    return RunCreateResponse(
        run_id=str(run.id),
        run_code=run.run_code,
        platform=run.platform,
        scenario_name=request.scenario_name,
        status=run.status.value,
        current_step=run.current_step,
        created_at=run.created_at,
    )


@router.get("/{run_id}", response_model=RunGetResponse)
async def get_run(
    run_id: UUID,
    db: Session = Depends(get_db),
):
    repo = RunRepository(db)
    run = repo.get_by_id(run_id)

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return RunGetResponse(
        run_id=str(run.id),
        run_code=run.run_code,
        platform=run.platform,
        status=run.status.value,
        current_step=run.current_step,
        strict_mode=run.strict_mode == "1",
        push_enabled=run.push_enabled == "1",
        seed=run.seed,
        metadata=run.metadata_json or {},
        started_at=run.started_at,
        ended_at=run.ended_at,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


@router.post("/{run_id}/advance", response_model=RunAdvanceResponse)
async def advance_run(
    run_id: UUID,
    request: RunAdvanceRequest,
    db: Session = Depends(get_db),
):
    repo = RunRepository(db)
    run = repo.get_by_id(run_id)

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if run.status not in (RunStatus.CREATED, RunStatus.RUNNING):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot advance run in status: {run.status.value}",
        )

    previous_step = run.current_step

    if run.status == RunStatus.CREATED:
        repo.update_status(run.id, RunStatus.RUNNING)
        run.status = RunStatus.RUNNING

    repo.advance_step(run.id)
    run.current_step += 1

    return RunAdvanceResponse(
        run_id=str(run.id),
        run_code=run.run_code,
        previous_step=previous_step,
        current_step=run.current_step,
        status=run.status.value,
        message=f"Advanced from step {previous_step} to {run.current_step}",
    )
