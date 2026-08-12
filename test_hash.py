from quarantine.hashing import calculate_sha256

file_path = "monitored_folder/sample.txt"

hash_value = calculate_sha256(file_path)

print("SHA256:")
print(hash_value)