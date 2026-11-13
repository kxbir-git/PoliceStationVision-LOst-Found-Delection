"""
Seed script — populates the database with realistic demo data.
Indian Police Station Lost & Found Portal
Run: python seed_data.py
"""

import sys
import os
from datetime import datetime, timedelta, timezone

# Ensure api directory is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))

from api.index import app, db, User, Property, Claim, AuditLog


def seed_database():
    with app.app_context():
        print("Recreating database tables...")
        db.drop_all()
        db.create_all()

        now = datetime.now(timezone.utc)

        # -------------------------------------------------------------
        # 1. Users
        # -------------------------------------------------------------
        print("Creating demo users...")
        officer = User(
            full_name="Inspector Rajesh Kumar",
            email="officer@demo.local",
            phone="9876543210",
            role="police",
            police_station="Kotwali Police Station, Lucknow",
            created_at=now - timedelta(days=60),
        )
        officer.set_password("demo1234")

        citizen1 = User(
            full_name="Priya Sharma",
            email="citizen1@demo.local",
            phone="9811223344",
            role="citizen",
            created_at=now - timedelta(days=45),
        )
        citizen1.set_password("demo1234")

        citizen2 = User(
            full_name="Amit Verma",
            email="citizen2@demo.local",
            phone="9822334455",
            role="citizen",
            created_at=now - timedelta(days=30),
        )
        citizen2.set_password("demo1234")

        db.session.add_all([officer, citizen1, citizen2])
        db.session.commit()

        # -------------------------------------------------------------
        # 2. Lost Properties (Citizen filed)
        # -------------------------------------------------------------
        print("Seeding Lost Property reports...")
        station = "Kotwali Police Station, Lucknow"

        lost_items = [
            Property(
                registration_number="LPR-2026-00001",
                type="lost",
                status="approved",
                reporter_id=citizen1.id,
                applicant_name="Priya Sharma",
                address="Flat 402, Shalimar Heights, Mahanagar, Lucknow",
                phone="9811223344",
                id_proof_type="Aadhaar",
                id_proof_masked="4821",
                category="Other",
                title="Blue Milton Water Bottle",
                description="1 litre stainless steel blue insulated bottle with minor scratches on bottom rim. Brand Milton Thermosteel.",
                how_lost="Left on table in Reference Section during exam preparation study hours.",
                date_lost=(now - timedelta(days=3)).strftime("%Y-%m-%d"),
                time_lost="14:30",
                location_lost="Lucknow University Tagore Library, 2nd Floor Reading Room",
                police_station=station,
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=3),
            ),
            Property(
                registration_number="LPR-2026-00002",
                type="lost",
                status="approved",
                reporter_id=citizen2.id,
                applicant_name="Amit Verma",
                address="12/48 Civil Lines, Lucknow",
                phone="9822334455",
                id_proof_type="PAN",
                id_proof_masked="7810",
                category="Electronic Devices",
                title="Samsung Galaxy M34 5G — Black",
                description="Dark black color, translucent back cover containing Rs. 100 note. IMEI on invoice. Lock pattern active.",
                how_lost="Fell from coat pocket while boarding city bus towards Charbagh.",
                date_lost=(now - timedelta(days=5)).strftime("%Y-%m-%d"),
                time_lost="09:15",
                location_lost="Qaiserbagh City Bus Stand, Platform 3",
                police_station=station,
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=5),
            ),
            Property(
                registration_number="LPR-2026-00003",
                type="lost",
                status="approved",
                reporter_id=citizen1.id,
                applicant_name="Priya Sharma",
                address="Flat 402, Shalimar Heights, Mahanagar, Lucknow",
                phone="9811223344",
                id_proof_type="Aadhaar",
                id_proof_masked="4821",
                category="Documents",
                title="Aadhaar Card — In name of Ramesh Kumar",
                description="Laminated original Aadhaar card belonging to my father Ramesh Kumar Sharma. Needed for bank verification.",
                how_lost="Misplaced document folder while booking reservation counter tickets.",
                date_lost=(now - timedelta(days=8)).strftime("%Y-%m-%d"),
                time_lost="16:00",
                location_lost="Charbagh Railway Station PRS Booking Counter",
                police_station=station,
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=8),
            ),
            Property(
                registration_number="LPR-2026-00004",
                type="lost",
                status="pending",
                reporter_id=citizen2.id,
                applicant_name="Amit Verma",
                address="12/48 Civil Lines, Lucknow",
                phone="9822334455",
                id_proof_type="DL",
                id_proof_masked="9234",
                category="Wallet / Purse",
                title="Brown Leather Wallet with Rs. 2000 cash",
                description="Woodland dark brown leather bifold wallet with SBI debit card, Lucknow Metro card, and approximately Rs. 2200 currency notes.",
                how_lost="Slipped out of rear trousers pocket while shopping at vegetable market.",
                date_lost=(now - timedelta(days=2)).strftime("%Y-%m-%d"),
                time_lost="19:40",
                location_lost="Hazratganj Main Market, near Mayfair Cinema",
                police_station=station,
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=2),
            ),
            Property(
                registration_number="LPR-2026-00005",
                type="lost",
                status="approved",
                reporter_id=citizen1.id,
                applicant_name="Priya Sharma",
                address="Flat 402, Shalimar Heights, Mahanagar, Lucknow",
                phone="9811223344",
                id_proof_type="VoterID",
                id_proof_masked="3391",
                category="Keys",
                title="Honda Activa Key with red rubber keychain",
                description="Single ignition key of Honda Activa 6G with red oval rubber key ring bearing text 'Lucknow Auto'.",
                how_lost="Keys fell between seat gap while unlocking parking stand.",
                date_lost=(now - timedelta(days=6)).strftime("%Y-%m-%d"),
                time_lost="11:30",
                location_lost="Gomti Nagar Metro Station Ground Parking",
                police_station=station,
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=6),
            ),
            Property(
                registration_number="LPR-2026-00006",
                type="lost",
                status="approved",
                reporter_id=citizen2.id,
                applicant_name="Amit Verma",
                address="12/48 Civil Lines, Lucknow",
                phone="9822334455",
                id_proof_type="PAN",
                id_proof_masked="7810",
                category="Jewellery",
                title="Gold Chain — 22 Karat, approx 10 grams",
                description="Traditional rope design gold chain with small Ganesha pendant. Hallmark stamp 916 near the S-hook clasp.",
                how_lost="Clasp became unfastened while walking along the jogging track.",
                date_lost=(now - timedelta(days=12)).strftime("%Y-%m-%d"),
                time_lost="06:45",
                location_lost="Ambedkar Memorial Park walkway, Vipin Khand",
                police_station=station,
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=12),
            ),
            Property(
                registration_number="LPR-2026-00007",
                type="lost",
                status="approved",
                reporter_id=citizen1.id,
                applicant_name="Priya Sharma",
                address="Flat 402, Shalimar Heights, Mahanagar, Lucknow",
                phone="9811223344",
                id_proof_type="Aadhaar",
                id_proof_masked="4821",
                category="Bags & Luggage",
                title="Black Wildcraft Backpack with HP Laptop",
                description="Grey-black 30L Wildcraft college bag containing HP 14-inch laptop, charger, notebook, and Aadhaar photocopy.",
                how_lost="Left beside tea kiosk while hiring an auto-rickshaw.",
                date_lost=(now - timedelta(days=15)).strftime("%Y-%m-%d"),
                time_lost="20:10",
                location_lost="Outside Charbagh Railway Station Exit Gate 2",
                police_station=station,
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=15),
            ),
            Property(
                registration_number="LPR-2026-00008",
                type="lost",
                status="returned",
                reporter_id=citizen2.id,
                applicant_name="Amit Verma",
                address="12/48 Civil Lines, Lucknow",
                phone="9822334455",
                id_proof_type="DL",
                id_proof_masked="9234",
                category="Documents",
                title="PAN Card — In name of Sunita Devi",
                description="Income tax permanent account number card in plastic transparent pouch.",
                how_lost="Dropped while ascending court chamber stairs.",
                date_lost=(now - timedelta(days=20)).strftime("%Y-%m-%d"),
                time_lost="12:00",
                location_lost="District & Sessions Court Compound, Lucknow",
                police_station=station,
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=20),
            ),
            Property(
                registration_number="LPR-2026-00009",
                type="lost",
                status="approved",
                reporter_id=citizen1.id,
                applicant_name="Priya Sharma",
                address="Flat 402, Shalimar Heights, Mahanagar, Lucknow",
                phone="9811223344",
                id_proof_type="Aadhaar",
                id_proof_masked="4821",
                category="Electronic Devices",
                title="HP Pavilion Laptop — Silver 14 inch",
                description="Intel Core i5, metallic silver body with Lucknow University departmental sticker on bottom chassis.",
                how_lost="Left in seminar hall after lecture presentation.",
                date_lost=(now - timedelta(days=7)).strftime("%Y-%m-%d"),
                time_lost="17:00",
                location_lost="Arts Faculty Block 1 Seminar Room, Lucknow University",
                police_station=station,
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=7),
            ),
        ]

        # -------------------------------------------------------------
        # 3. Unclaimed Properties / In Police Custody
        # -------------------------------------------------------------
        print("Seeding Unclaimed Property / Police Custody records...")
        unclaimed_items = [
            Property(
                registration_number="UCP-2026-00001",
                type="unclaimed",
                status="approved",
                reporter_id=officer.id,
                applicant_name="Inspector Rajesh Kumar (Police Duty)",
                address="Kotwali Police Station, Lucknow",
                phone="9876543210",
                category="Electronic Devices",
                title="Nokia Keypad Phone — Black Model 105",
                description="Basic feature mobile phone with Airtel SIM card. Battery 40%, no security passcode. Display intact.",
                how_lost="Handed over to beat constable by tea vendor Shri Ram Prasad.",
                date_lost=(now - timedelta(days=4)).strftime("%Y-%m-%d"),
                location_lost="Aminabad Main Bus Stop bench",
                police_station=station,
                officer_name="Inspector Rajesh Kumar",
                officer_badge_id="UPP-LK-4821",
                current_location="Station Malkhana Locker #3",
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=4),
            ),
            Property(
                registration_number="UCP-2026-00002",
                type="unclaimed",
                status="approved",
                reporter_id=officer.id,
                applicant_name="Inspector Rajesh Kumar (Police Duty)",
                address="Kotwali Police Station, Lucknow",
                phone="9876543210",
                category="Bags & Luggage",
                title="Blue Wildcraft School / College Backpack",
                description="Dark navy blue Wildcraft backpack containing class 12 revision notes, steel tiffin box, and empty pencil case.",
                how_lost="Found unattended on waiting room seating row 4.",
                date_lost=(now - timedelta(days=9)).strftime("%Y-%m-%d"),
                location_lost="Charbagh Railway Station Upper Class Waiting Hall",
                police_station=station,
                officer_name="Inspector Rajesh Kumar",
                officer_badge_id="UPP-LK-4821",
                current_location="Station Records Room, Shelf B",
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=9),
            ),
            Property(
                registration_number="UCP-2026-00003",
                type="unclaimed",
                status="approved",
                reporter_id=officer.id,
                applicant_name="Inspector Rajesh Kumar (Police Duty)",
                address="Kotwali Police Station, Lucknow",
                phone="9876543210",
                category="Documents",
                title="Voter ID Card — In name of Meera Patel",
                description="Election Commission of India EPIC Card No. UP/48/201/049182. Original laminated card.",
                how_lost="Found on post office customer writing desk by postal assistant.",
                date_lost=(now - timedelta(days=11)).strftime("%Y-%m-%d"),
                location_lost="Mahanagar Head Post Office Counter",
                police_station=station,
                officer_name="Inspector Rajesh Kumar",
                officer_badge_id="UPP-LK-4821",
                current_location="Duty Officer Desk Drawer 2",
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=11),
            ),
            Property(
                registration_number="UCP-2026-00004",
                type="unclaimed",
                status="approved",
                reporter_id=officer.id,
                applicant_name="Inspector Rajesh Kumar (Police Duty)",
                address="Kotwali Police Station, Lucknow",
                phone="9876543210",
                category="Wallet / Purse",
                title="Ladies Purse — Maroon Leather with cash Rs. 1450",
                description="Maroon faux-leather ladies purse containing Rs. 1450 cash, Metro smart card, and safety pins.",
                how_lost="Found under clothing display rack in Janpath market.",
                date_lost=(now - timedelta(days=3)).strftime("%Y-%m-%d"),
                location_lost="Janpath Shopping Complex, Hazratganj",
                police_station=station,
                officer_name="Inspector Rajesh Kumar",
                officer_badge_id="UPP-LK-4821",
                current_location="Station Malkhana Locker #1",
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=3),
            ),
            Property(
                registration_number="UCP-2026-00005",
                type="unclaimed",
                status="approved",
                reporter_id=officer.id,
                applicant_name="Inspector Rajesh Kumar (Police Duty)",
                address="Kotwali Police Station, Lucknow",
                phone="9876543210",
                category="Keys",
                title="Bunch of 4 Keys with Godrej Brass Tag",
                description="Four iron keys on steel split ring with rectangular brass tag marked 'Godrej Nav-Tal'.",
                how_lost="Recovered by traffic home guard at busy pedestrian crosswalk.",
                date_lost=(now - timedelta(days=1)).strftime("%Y-%m-%d"),
                location_lost="Hazratganj Main Traffic Signal Crossing",
                police_station=station,
                officer_name="Inspector Rajesh Kumar",
                officer_badge_id="UPP-LK-4821",
                current_location="Duty Officer Key Rack #7",
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=1),
            ),
            Property(
                registration_number="UCP-2026-00006",
                type="unclaimed",
                status="approved",
                reporter_id=officer.id,
                applicant_name="Inspector Rajesh Kumar (Police Duty)",
                address="Kotwali Police Station, Lucknow",
                phone="9876543210",
                category="Jewellery",
                title="Silver Anklet (Chandi ki Payal) — Single piece",
                description="Single piece traditional silver payal with small bells (ghunghroo), weight approx 45 grams.",
                how_lost="Found near ladies bus shelter seat.",
                date_lost=(now - timedelta(days=14)).strftime("%Y-%m-%d"),
                location_lost="Aminabad Main Bus Terminus",
                police_station=station,
                officer_name="Inspector Rajesh Kumar",
                officer_badge_id="UPP-LK-4821",
                current_location="Station Malkhana Locker #5",
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=14),
            ),
            Property(
                registration_number="UCP-2026-00007",
                type="unclaimed",
                status="approved",
                reporter_id=officer.id,
                applicant_name="Inspector Rajesh Kumar (Police Duty)",
                address="Kotwali Police Station, Lucknow",
                phone="9876543210",
                category="Vehicles",
                title="Hero Cycle — Black, Ladies 26T Model",
                description="Black colored Hero Miss India bicycle with front basket, bell, and reflective rear sticker. Frame number recorded in station register.",
                how_lost="Abandoned parked at public crossing for over 5 days.",
                date_lost=(now - timedelta(days=18)).strftime("%Y-%m-%d"),
                location_lost="IT Crossing Flyover Pillar No. 12",
                police_station=station,
                officer_name="Inspector Rajesh Kumar",
                officer_badge_id="UPP-LK-4821",
                current_location="Police Station Compound Vehicle Shed",
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=18),
            ),
            Property(
                registration_number="UCP-2026-00008",
                type="unclaimed",
                status="approved",
                reporter_id=officer.id,
                applicant_name="Inspector Rajesh Kumar (Police Duty)",
                address="Kotwali Police Station, Lucknow",
                phone="9876543210",
                category="Books / Stationery",
                title="NCERT Class 12 Physics Textbook (Part 1)",
                description="Paperback CBSE NCERT Physics textbook with brown paper binding and roll number '12-B-14' written on index page.",
                how_lost="Left behind on city bus seat.",
                date_lost=(now - timedelta(days=6)).strftime("%Y-%m-%d"),
                location_lost="CMS Gomti Nagar School Bus Stop",
                police_station=station,
                officer_name="Inspector Rajesh Kumar",
                officer_badge_id="UPP-LK-4821",
                current_location="Station Records Room",
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=6),
            ),
            Property(
                registration_number="UCP-2026-00009",
                type="unclaimed",
                status="approved",
                reporter_id=officer.id,
                applicant_name="Inspector Rajesh Kumar (Police Duty)",
                address="Kotwali Police Station, Lucknow",
                phone="9876543210",
                category="Clothing / Accessories",
                title="Red Silk Dupatta with Golden Border (Zari work)",
                description="Pure red silk traditional dupatta with 2-inch golden zari embroidery border, approx 2.5 metres length.",
                how_lost="Found near ticket counter queue railing.",
                date_lost=(now - timedelta(days=10)).strftime("%Y-%m-%d"),
                location_lost="Lucknow Zoo Main Entrance Gate",
                police_station=station,
                officer_name="Inspector Rajesh Kumar",
                officer_badge_id="UPP-LK-4821",
                current_location="Station Malkhana Locker #2",
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=10),
            ),
            Property(
                registration_number="UCP-2026-00010",
                type="unclaimed",
                status="approved",
                reporter_id=officer.id,
                applicant_name="Inspector Rajesh Kumar (Police Duty)",
                address="Kotwali Police Station, Lucknow",
                phone="9876543210",
                category="Documents",
                title="Driving License — In name of Vikram Singh",
                description="UP Transport Department smart card driving license for Non-Transport LMV/MCWG.",
                how_lost="Found on shop counter and deposited by merchant association.",
                date_lost=(now - timedelta(days=5)).strftime("%Y-%m-%d"),
                location_lost="Aliganj Sector C Market Complex",
                police_station=station,
                officer_name="Inspector Rajesh Kumar",
                officer_badge_id="UPP-LK-4821",
                current_location="Duty Officer Desk",
                declaration_accepted=True,
                consent_accepted=True,
                created_at=now - timedelta(days=5),
            ),
        ]

        db.session.add_all(lost_items)
        db.session.add_all(unclaimed_items)
        db.session.commit()

        # -------------------------------------------------------------
        # 4. Claims (Citizen claims property)
        # -------------------------------------------------------------
        print("Seeding citizen claims...")
        # Citizen 2 claims the maroon ladies purse for his mother
        claim1 = Claim(
            property_id=unclaimed_items[3].id,  # Maroon purse
            claimant_id=citizen2.id,
            status="pending",
            message="This maroon purse belongs to my mother Smt. Geeta Verma who was shopping at Janpath market on Tuesday. It contains a Lucknow Metro smart card with card number ending in 9102 and approximately Rs. 1400 in cash.",
            created_at=now - timedelta(days=1),
        )

        # Citizen 1 claimed lost PAN card which was verified and returned
        claim2 = Claim(
            property_id=lost_items[7].id,  # PAN card
            claimant_id=citizen2.id,
            status="approved",
            message="Verified ownership via Aadhaar and family ration card copy at Kotwali Police Station duty desk.",
            created_at=now - timedelta(days=10),
        )

        db.session.add_all([claim1, claim2])
        db.session.commit()

        # -------------------------------------------------------------
        # 5. Station Audit Logs
        # -------------------------------------------------------------
        print("Seeding Police Station audit trail...")
        audit_entries = [
            AuditLog(
                officer_id=officer.id,
                property_id=lost_items[0].id,
                action="Verification & Approval of Lost Property Report",
                old_value="pending",
                new_value="approved",
                timestamp=now - timedelta(days=3),
            ),
            AuditLog(
                officer_id=officer.id,
                property_id=lost_items[1].id,
                action="Jurisdiction Verification & Approval",
                old_value="pending",
                new_value="approved",
                timestamp=now - timedelta(days=5),
            ),
            AuditLog(
                officer_id=officer.id,
                property_id=lost_items[7].id,
                claim_id=claim2.id,
                action="Physical Verification & Restoration to Legal Owner",
                old_value="approved",
                new_value="returned",
                timestamp=now - timedelta(days=8),
            ),
            AuditLog(
                officer_id=officer.id,
                property_id=unclaimed_items[0].id,
                action="Custody Entry Recorded in Station Malkhana Register",
                old_value="intake",
                new_value="approved",
                timestamp=now - timedelta(days=4),
            ),
            AuditLog(
                officer_id=officer.id,
                property_id=unclaimed_items[3].id,
                claim_id=claim1.id,
                action="Claim Registered — Notice issued to claimant for physical verification",
                old_value="unclaimed",
                new_value="claim_pending",
                timestamp=now - timedelta(days=1),
            ),
        ]

        db.session.add_all(audit_entries)
        db.session.commit()

        print("=" * 60)
        print("Database successfully seeded!")
        print("=" * 60)
        print("Police Officer Account:")
        print("  Email:    officer@demo.local")
        print("  Password: demo1234")
        print("  Station:  Kotwali Police Station, Lucknow")
        print("\nCitizen Accounts:")
        print("  1. Priya Sharma: citizen1@demo.local / demo1234")
        print("  2. Amit Verma:   citizen2@demo.local / demo1234")
        print(f"\nTotal Lost Properties:      {len(lost_items)}")
        print(f"Total Unclaimed Properties: {len(unclaimed_items)}")
        print(f"Total Claims:               {len([claim1, claim2])}")
        print(f"Total Audit Log Entries:    {len(audit_entries)}")
        print("=" * 60)


if __name__ == "__main__":
    seed_database()
