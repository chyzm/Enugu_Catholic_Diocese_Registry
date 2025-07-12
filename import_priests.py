import csv
from django.contrib.auth.models import User, Group
from registry.models import PriestProfile, Parish

csv_file_path = 'priest.csv'
export_file_path = 'created_priests.csv'

created_users = []

with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        full_name = row.get('full_name', '').strip()
        email = row.get('email', '').strip().lower()
        parish_name = row.get('parish', '').strip()

        if not full_name or not email:
            print(f"❌ Skipping row: missing full_name or email")
            continue

        username = email.split('@')[0]

        try:
            parish = Parish.objects.get(name__iexact=parish_name)
        except Parish.DoesNotExist:
            print(f"❌ Skipping '{full_name}': parish '{parish_name}' not found")
            continue

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': full_name.split()[0],
                'last_name': ' '.join(full_name.split()[1:]),
                'is_staff': True
            }
        )

        if not created:
            print(f"⚠️ User '{username}' already exists")
            continue

        default_password = 'changeme123'
        user.set_password(default_password)
        user.save()

        group, _ = Group.objects.get_or_create(name='Priest')
        user.groups.add(group)

        PriestProfile.objects.create(user=user, parish=parish)

        print(f"✅ Created PriestProfile for '{username}' in '{parish_name}'")

        # Store for export
        created_users.append({
            'username': username,
            'email': email,
            'default_password': default_password,
            'parish': parish_name,
            'full_name': full_name
        })

# Write to CSV
if created_users:
    with open(export_file_path, 'w', newline='', encoding='utf-8') as export_file:
        writer = csv.DictWriter(export_file, fieldnames=['full_name', 'username', 'email', 'default_password', 'parish'])
        writer.writeheader()
        for user in created_users:
            writer.writerow(user)

    print(f"\n📁 Exported created users to '{export_file_path}'")
else:
    print("\nℹ️ No new users were created, nothing to export.")
