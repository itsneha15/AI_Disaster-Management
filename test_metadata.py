from quarantine.metadata_manager import add_file_metadata

entry = {
    "id": 1,
    "original_name": "sample.txt",
    "stored_name": "QF_000001.enc",
    "hash": "123456789ABC",
    "risk": "Critical",
    "status": "Quarantined"
}

add_file_metadata(entry)

print("Metadata Added Successfully!")