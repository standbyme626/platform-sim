import csv
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
import string


class ProductBuilder:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.products: List[Dict[str, Any]] = []
    
    def generate_products(self, count: int = 100) -> List[Dict[str, Any]]:
        categories = ["电子产品", "服装", "食品", "家居", "美妆", "运动", "图书", "玩具"]
        
        for i in range(count):
            category = random.choice(categories)
            product = {
                "id": f"product_{i+1:04d}",
                "name": f"{category}商品_{i+1:04d}",
                "default_code": f"SKU_{i+1:04d}",
                "categ_id": f"cat_{categories.index(category)+1}",
                "list_price": round(random.uniform(10, 1000), 2),
                "standard_price": round(random.uniform(5, 500), 2),
                "type": "product",
                "sale_ok": True,
                "purchase_ok": True,
                "active": True,
            }
            self.products.append(product)
        
        return self.products
    
    def to_csv(self, filename: str = "product.template.csv"):
        filepath = self.output_dir / filename
        
        fieldnames = [
            "External ID", "Name", "Internal Reference", "Category",
            "Sales Price", "Cost", "Product Type", "Can be Sold",
            "Can be Purchased", "Active",
        ]
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for p in self.products:
                writer.writerow({
                    "External ID": p["id"],
                    "Name": p["name"],
                    "Internal Reference": p["default_code"],
                    "Category": p["categ_id"],
                    "Sales Price": p["list_price"],
                    "Cost": p["standard_price"],
                    "Product Type": p["type"],
                    "Can be Sold": p["sale_ok"],
                    "Can be Purchased": p["purchase_ok"],
                    "Active": p["active"],
                })
        
        return filepath


class PartnerBuilder:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.partners: List[Dict[str, Any]] = []
    
    def generate_customers(self, count: int = 500) -> List[Dict[str, Any]]:
        first_names = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
        last_names = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军"]
        provinces = ["浙江省", "江苏省", "广东省", "北京市", "上海市", "四川省", "湖北省", "山东省"]
        cities = ["杭州市", "南京市", "广州市", "北京市", "上海市", "成都市", "武汉市", "济南市"]
        
        for i in range(count):
            name = f"{random.choice(first_names)}{random.choice(last_names)}"
            province_idx = random.randint(0, len(provinces) - 1)
            
            partner = {
                "id": f"customer_{i+1:04d}",
                "name": name,
                "phone": f"1{random.choice(['3', '5', '7', '8', '9'])}{random.randint(100000000, 999999999)}",
                "email": f"{name.lower()}@example.com",
                "street": f"{random.randint(1, 999)}号",
                "city": cities[province_idx],
                "state_id": provinces[province_idx],
                "zip": f"{random.randint(100000, 999999)}",
                "customer_rank": random.randint(1, 10),
                "supplier_rank": 0,
                "is_company": False,
            }
            self.partners.append(partner)
        
        return self.partners
    
    def to_csv(self, filename: str = "res.partner.csv"):
        filepath = self.output_dir / filename
        
        fieldnames = [
            "External ID", "Name", "Phone", "Email", "Street",
            "City", "State", "Zip", "Customer Rank", "Supplier Rank", "Is a Company",
        ]
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for p in self.partners:
                writer.writerow({
                    "External ID": p["id"],
                    "Name": p["name"],
                    "Phone": p["phone"],
                    "Email": p["email"],
                    "Street": p["street"],
                    "City": p["city"],
                    "State": p["state_id"],
                    "Zip": p["zip"],
                    "Customer Rank": p["customer_rank"],
                    "Supplier Rank": p["supplier_rank"],
                    "Is a Company": p["is_company"],
                })
        
        return filepath


class OrderBuilder:
    def __init__(self, output_dir: Path, products: List[Dict], partners: List[Dict]):
        self.output_dir = output_dir
        self.products = products
        self.partners = partners
        self.orders: List[Dict[str, Any]] = []
        self.order_lines: List[Dict[str, Any]] = []
    
    def generate_orders(self, count: int = 1000) -> List[Dict[str, Any]]:
        statuses = ["draft", "sent", "sale", "done", "cancel"]
        status_weights = [10, 20, 40, 25, 5]
        
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(count):
            customer = random.choice(self.partners)
            status = random.choices(statuses, weights=status_weights)[0]
            order_date = base_date + timedelta(days=random.randint(0, 365))
            
            num_lines = random.randint(1, 5)
            lines = []
            total = 0
            
            for j in range(num_lines):
                product = random.choice(self.products)
                quantity = random.randint(1, 10)
                price = product["list_price"]
                subtotal = quantity * price
                total += subtotal
                
                line = {
                    "id": f"order_line_{i+1:04d}_{j+1}",
                    "order_id": f"order_{i+1:04d}",
                    "product_id": product["id"],
                    "name": product["name"],
                    "product_uom_qty": quantity,
                    "price_unit": price,
                    "price_subtotal": subtotal,
                }
                lines.append(line)
                self.order_lines.append(line)
            
            order = {
                "id": f"order_{i+1:04d}",
                "name": f"SO{i+1:05d}",
                "partner_id": customer["id"],
                "date_order": order_date.strftime("%Y-%m-%d %H:%M:%S"),
                "state": status,
                "amount_total": round(total, 2),
                "amount_untaxed": round(total / 1.13, 2),
                "amount_tax": round(total - total / 1.13, 2),
            }
            self.orders.append(order)
        
        return self.orders
    
    def to_csv(self, order_filename: str = "sale.order.csv", line_filename: str = "sale.order.line.csv"):
        order_filepath = self.output_dir / order_filename
        line_filepath = self.output_dir / line_filename
        
        order_fieldnames = [
            "External ID", "Order Reference", "Customer", "Order Date",
            "Status", "Total", "Untaxed Amount", "Tax Amount",
        ]
        
        with open(order_filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=order_fieldnames)
            writer.writeheader()
            
            for o in self.orders:
                writer.writerow({
                    "External ID": o["id"],
                    "Order Reference": o["name"],
                    "Customer": o["partner_id"],
                    "Order Date": o["date_order"],
                    "Status": o["state"],
                    "Total": o["amount_total"],
                    "Untaxed Amount": o["amount_untaxed"],
                    "Tax Amount": o["amount_tax"],
                })
        
        line_fieldnames = [
            "External ID", "Order", "Product", "Description",
            "Quantity", "Unit Price", "Subtotal",
        ]
        
        with open(line_filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=line_fieldnames)
            writer.writeheader()
            
            for l in self.order_lines:
                writer.writerow({
                    "External ID": l["id"],
                    "Order": l["order_id"],
                    "Product": l["product_id"],
                    "Description": l["name"],
                    "Quantity": l["product_uom_qty"],
                    "Unit Price": l["price_unit"],
                    "Subtotal": l["price_subtotal"],
                })
        
        return order_filepath, line_filepath


class InventoryBuilder:
    def __init__(self, output_dir: Path, products: List[Dict]):
        self.output_dir = output_dir
        self.products = products
        self.quants: List[Dict[str, Any]] = []
    
    def generate_inventory(self) -> List[Dict[str, Any]]:
        warehouses = ["WH_MAIN", "WH_EAST", "WH_WEST", "WH_NORTH", "WH_SOUTH"]
        locations = ["LOC_A01", "LOC_A02", "LOC_B01", "LOC_B02", "LOC_C01"]
        
        for product in self.products:
            num_warehouses = random.randint(1, 3)
            selected_warehouses = random.sample(warehouses, num_warehouses)
            
            for wh in selected_warehouses:
                quant = {
                    "id": f"quant_{product['id']}_{wh}",
                    "product_id": product["id"],
                    "location_id": f"{wh}/{random.choice(locations)}",
                    "quantity": random.randint(0, 500),
                    "reserved_quantity": random.randint(0, 50),
                }
                quant["available_quantity"] = quant["quantity"] - quant["reserved_quantity"]
                self.quants.append(quant)
        
        return self.quants
    
    def to_csv(self, filename: str = "stock.quant.csv"):
        filepath = self.output_dir / filename
        
        fieldnames = [
            "External ID", "Product", "Location", "Quantity",
            "Reserved Quantity", "Available Quantity",
        ]
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for q in self.quants:
                writer.writerow({
                    "External ID": q["id"],
                    "Product": q["product_id"],
                    "Location": q["location_id"],
                    "Quantity": q["quantity"],
                    "Reserved Quantity": q["reserved_quantity"],
                    "Available Quantity": q["available_quantity"],
                })
        
        return filepath


def build_all(output_dir: str = "output/odoo_seed"):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("Building products...")
    product_builder = ProductBuilder(output_path)
    products = product_builder.generate_products(100)
    product_builder.to_csv()
    
    print("Building partners...")
    partner_builder = PartnerBuilder(output_path)
    partners = partner_builder.generate_customers(500)
    partner_builder.to_csv()
    
    print("Building orders...")
    order_builder = OrderBuilder(output_path, products, partners)
    orders = order_builder.generate_orders(1000)
    order_builder.to_csv()
    
    print("Building inventory...")
    inventory_builder = InventoryBuilder(output_path, products)
    inventory_builder.generate_inventory()
    inventory_builder.to_csv()
    
    print(f"Done! Files written to {output_path}")
    
    return {
        "products": len(products),
        "partners": len(partners),
        "orders": len(orders),
        "order_lines": len(order_builder.order_lines),
        "quants": len(inventory_builder.quants),
    }


if __name__ == "__main__":
    build_all()
