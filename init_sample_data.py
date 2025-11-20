"""
Initialize the database with sample data for testing and demonstration
Run this script once to populate your database with example campers, attributes, and settings.
"""

from database import Attribute, Base, Camper, SessionLocal, Settings, engine


def init_sample_data():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(Camper).first():
            print("Database already contains data. Skipping initialization.")
            return

        print("Initializing database with sample data...")

        # Create Settings
        settings = Settings(
            charge_type="per_day",
            auto_accept_bookings=True,
            business_name="Truckify Truck Rentals",
            business_email="info@truckify.com",
            business_phone="+31 6 12345678",
            company_color="#3B82F6",
            company_logo=None,  # Can be set in settings page
            language="en",
            booking_page_language="en",
            minimum_booking_days=1,
            maximum_booking_days=30,
        )
        db.add(settings)

        # Create Sample Trucks
        campers = [
            Camper(
                name="VW California Ocean",
                license_plate="TR-001-VW",
                price_per_day=125.00,
                color="#3B82F6",  # Blue
                description="Luxurious VW California Ocean with all amenities. Perfect for couples or small families. Features a pop-up roof, kitchen, and comfortable sleeping arrangements.",
                facilities=[
                    "Kitchen",
                    "Shower",
                    "Heating",
                    "Pop-up Roof",
                    "Solar Panel",
                    "Fridge",
                ],
                images=[
                    "https://images.unsplash.com/photo-1527786356703-4b100091cd2c?w=800"
                ],
                max_passengers=4,
                year=2022,
                is_active=True,
            ),
            Camper(
                name="Mercedes-Benz Marco Polo",
                license_plate="TR-002-MB",
                price_per_day=145.00,
                color="#10B981",  # Green
                description="Premium Mercedes-Benz Marco Polo with sophisticated design and top-notch comfort. Ideal for luxury camping experiences.",
                facilities=[
                    "Kitchen",
                    "Heating",
                    "Air Conditioning",
                    "Awning",
                    "Parking Sensors",
                    "LED Lighting",
                ],
                images=[
                    "https://images.unsplash.com/photo-1464219789935-c2d9d9aba644?w=800"
                ],
                max_passengers=4,
                year=2023,
                is_active=True,
            ),
            Camper(
                name="Fiat Ducato Camper",
                license_plate="TR-003-FI",
                price_per_day=95.00,
                color="#F59E0B",  # Orange
                description="Spacious and practical Fiat Ducato conversion. Great value for money with plenty of room for the whole family.",
                facilities=[
                    "Kitchen",
                    "Shower",
                    "Toilet",
                    "Heating",
                    "Large Bed",
                    "Storage",
                ],
                images=[
                    "https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?w=800"
                ],
                max_passengers=5,
                year=2021,
                is_active=True,
            ),
            Camper(
                name="Ford Transit Custom Camper",
                license_plate="TR-004-FO",
                price_per_day=110.00,
                color="#8B5CF6",  # Purple
                description="Modern Ford Transit Custom conversion with smart layout and great fuel efficiency. Perfect for weekend getaways.",
                facilities=[
                    "Kitchen",
                    "Heating",
                    "Swivel Seats",
                    "USB Charging",
                    "LED Lights",
                ],
                images=[
                    "https://images.unsplash.com/photo-1527847263472-aa5338d178b8?w=800"
                ],
                max_passengers=2,
                year=2022,
                is_active=True,
            ),
            Camper(
                name="Peugeot Boxer Adventure",
                license_plate="TR-005-PE",
                price_per_day=105.00,
                color="#EF4444",  # Red
                description="Rugged Peugeot Boxer ready for adventure. Built for exploring off the beaten path with reliable performance.",
                facilities=[
                    "Kitchen",
                    "Shower",
                    "Solar Panel",
                    "Bike Rack",
                    "Outdoor Table",
                    "Awning",
                ],
                images=[
                    "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800"
                ],
                max_passengers=4,
                year=2021,
                is_active=True,
            ),
        ]

        for camper in campers:
            db.add(camper)

        # Create Sample Attributes (Add-ons)
        attributes = [
            Attribute(
                name="Porta-Potty",
                description="Portable toilet for your convenience during camping",
                price=15.00,
                is_active=True,
            ),
            Attribute(
                name="Bike Rack",
                description="External bike rack to carry up to 2 bicycles",
                price=10.00,
                is_active=True,
            ),
            Attribute(
                name="Camping Chairs & Table",
                description="Outdoor furniture set with 4 chairs and a foldable table",
                price=12.00,
                is_active=True,
            ),
            Attribute(
                name="BBQ Grill",
                description="Portable BBQ grill for outdoor cooking",
                price=8.00,
                is_active=True,
            ),
            Attribute(
                name="Bedding Package",
                description="Complete bedding set including sheets, pillows, and blankets",
                price=20.00,
                is_active=True,
            ),
            Attribute(
                name="Child Seat",
                description="Safety child seat (specify age when booking)",
                price=5.00,
                is_active=True,
            ),
            Attribute(
                name="GPS Navigation",
                description="Garmin GPS device with European maps",
                price=7.00,
                is_active=True,
            ),
            Attribute(
                name="Camping Gas",
                description="Extra camping gas bottle",
                price=15.00,
                is_active=True,
            ),
        ]

        for attribute in attributes:
            db.add(attribute)

        db.commit()
        print("✅ Sample data initialized successfully!")
        print(f"   - Created {len(campers)} sample trucks")
        print(f"   - Created {len(attributes)} sample add-ons")
        print("   - Created business settings")
        print("\nYou can now start using Truckify!")
        print("Dashboard: http://localhost:3000/dashboard")
        print("Booking Page: http://localhost:3000/book")

    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_sample_data()
