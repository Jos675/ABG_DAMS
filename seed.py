#!/usr/bin/env python3

import os
from app.database import SessionLocal
from app import crud, models, schemas
from app.models import Role, Classification
import pandas as pd

def seed_data():
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = crud.get_user_by_username(db, "admin")
        if not admin:
            # Create admin user
            admin = crud.create_user(db, schemas.UserCreate(
                username="admin",
                email="admin@example.com",
                password="admin123",
                role=Role.admin
            ))
            print("Created admin user")
        else:
            print("Admin user already exists")

        # Check if Excel data has already been imported
        excel_assets = db.query(models.Asset).filter(models.Asset.title.like("Record %")).count()
        if excel_assets > 0:
            print(f"Excel data already imported ({excel_assets} records). Skipping import.")
            return

        # Read Excel data
        excel_path = r"c:\Users\KTF-RBBAS24-092\Downloads\ARG Archives Database 2019.xlsx"
        df = pd.read_excel(excel_path, sheet_name='Records')
        
        print(f"Found {len(df)} records in Excel file")
        
        # Import records as assets
        for index, row in df.iterrows():
            try:
                # Determine classification
                confidential = str(row.get('Confidential?', '')).strip().upper()
                if confidential == 'YES':
                    classification = Classification.confidential
                else:
                    classification = Classification.regular
                
                # Create title from file titles
                title_l3 = str(row.get('File Title L3', '')).strip()
                title_l4 = str(row.get('File Title L4', '')).strip()
                title = title_l3
                if title_l4 and title_l4 != 'nan':
                    title += f" - {title_l4}"
                if not title or title == 'nan':
                    title = f"Record {row.get('Record ID', index+1)}"
                
                # Description from comments
                description = str(row.get('Comments', '')).strip()
                if description == 'nan':
                    description = None
                
                # Tags from keywords
                keywords = str(row.get('Keywords', '')).strip()
                tags = None
                if keywords and keywords != 'nan':
                    tags = [kw.strip() for kw in keywords.split(',') if kw.strip()]
                
                # Create asset
                asset = crud.create_asset(
                    db=db,
                    asset=schemas.AssetCreate(
                        title=title,
                        description=description,
                        tags=tags,
                        classification=classification
                    ),
                    file_path=f"archives/{row.get('Record ID', f'record_{index+1}')}.pdf",  # placeholder
                    filename=f"{row.get('Record ID', f'record_{index+1}')}.pdf",
                    original_filename=f"{row.get('Record ID', f'record_{index+1}')}.pdf",
                    file_type="application/pdf",  # placeholder
                    size=0,  # placeholder
                    owner_id=admin.id
                )
                
                if (index + 1) % 100 == 0:
                    print(f"Imported {index + 1} assets...")
                    
            except Exception as e:
                print(f"Error importing row {index}: {e}")
                continue
        
        print(f"Successfully imported {len(df)} assets from Excel")

    finally:
        db.close()

if __name__ == "__main__":
    seed_data()