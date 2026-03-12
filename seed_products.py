import uuid
from qdrant_manager import QdrantManager
from qdrant_client.http import models

def seed_products():
    qm = QdrantManager()
    
    # The collection 'products' is already created by QdrantManager.__init__
    # We just need to ensure it's ready for upserting
    
    products = [
        # Laptops
        {"id": "L001", "name": "MacBook Pro 16", "category": "Laptops", "price": 2499, "stock": 5, "description": "M3 Max, 32GB RAM, 1TB SSD. Professional-grade performance for video editing and 3D rendering."},
        {"id": "L002", "name": "Dell XPS 15", "category": "Laptops", "price": 1899, "stock": 10, "description": "Intel i9, 32GB RAM, 1TB SSD. Premium design with a stunning 4K OLED display for creators."},
        {"id": "L003", "name": "Razer Blade 16", "category": "Laptops", "price": 2999, "stock": 2, "description": "RTX 4090, 32GB RAM, 1TB SSD. High-performance gaming laptop with a dual-mode Mini-LED display."},
        {"id": "L004", "name": "ASUS ROG Zephyrus G14", "category": "Laptops", "price": 1599, "stock": 8, "description": "Compact 14-inch gaming laptop with Ryzen 9 and RTX 4060. Great for portable gaming."},
        {"id": "L005", "name": "HP Spectre x360", "category": "Laptops", "price": 1399, "stock": 12, "description": "2-in-1 convertible laptop with Intel i7 and a touch screen. Versatile for work and play."},
        
        # Monitors
        {"id": "M001", "name": "LG UltraFine 5K", "category": "Monitors", "price": 1299, "stock": 3, "description": "27-inch 5K Display with Thunderbolt 3. Ideal for Mac users and graphic designers."},
        {"id": "M002", "name": "Samsung Odyssey G9", "category": "Monitors", "price": 1499, "stock": 4, "description": "49-inch Dual QHD Curved Gaming Monitor with 240Hz. Ultra-wide immersive experience."},
        {"id": "M003", "name": "Dell UltraSharp 32", "category": "Monitors", "price": 899, "stock": 7, "description": "4K USB-C Hub Monitor with IPS Black technology for superior contrast and color."},
        
        # Accessories
        {"id": "A001", "name": "Logitech MX Master 3S", "category": "Accessories", "price": 99, "stock": 50, "description": "Ergonomic wireless mouse with quiet clicks and an 8K DPI sensor. Productivity focused."},
        {"id": "A002", "name": "Apple Magic Keyboard", "category": "Accessories", "price": 199, "stock": 20, "description": "Wireless keyboard with Touch ID and a numeric keypad. Optimized for macOS."},
        {"id": "A003", "name": "Sony WH-1000XM5", "category": "Accessories", "price": 399, "stock": 15, "description": "Premium noise-canceling headphones with exceptional sound quality and comfort."},
        {"id": "A004", "name": "Blue Yeti USB Microphone", "category": "Accessories", "price": 129, "stock": 25, "description": "Professional multi-pattern USB microphone for podcasting, streaming, and recording."},
        {"id": "A005", "name": "CalDigit TS4 Dock", "category": "Accessories", "price": 399, "stock": 10, "description": "Thunderbolt 4 Dock with 18 ports. The ultimate connectivity solution for any workspace."},
        {"id": "A006", "name": "Elgato Stream Deck MK.2", "category": "Accessories", "price": 149, "stock": 15, "description": "Studio controller with 15 customizable LCD keys for apps, tools, and platforms."}
    ]

    points = []
    for p in products:
        text = f"{p['name']} {p['category']} {p['description']} Price: ${p['price']}"
        vector = qm.get_embedding(text)
        points.append(
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector={"text_vector": vector, "context_vector": vector},
                payload=p
            )
        )
    
    qm.qdrant.upsert(
        collection_name="products",
        points=points
    )
    print(f"Seeded {len(products)} products into Qdrant.")

if __name__ == "__main__":
    seed_products()
