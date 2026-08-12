from quarantine.repository import show_repository

while True:

    print("\n")
    print("=" * 45)
    print(" AI-Assisted Secure Quarantine System ")
    print("=" * 45)

    print("1. Scan Folder")

    print("2. View Quarantined Files")

    print("3. Restore File")

    print("4. Delete Permanently")

    print("5. View Logs")

    print("6. Exit")

    choice = input("\nEnter Choice : ")

    if choice == "1":

        print("\nScanning Module Coming Next...")

    elif choice == "2":

        show_repository()

    elif choice == "3":

        print("\nRestore Module Coming Next...")

    elif choice == "4":

        print("\nDelete Module Coming Next...")

    elif choice == "5":

        print("\nLog Viewer Coming Next...")

    elif choice == "6":

        print("\nThank You")

        break

    else:

        print("\nInvalid Choice")