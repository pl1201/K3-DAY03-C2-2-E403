"""
Script sinh du lieu thuc te cho Cupid Agent
Su dung Faker + realistic Vietnamese names and data
"""

import json
import random
from faker import Faker

fake = Faker('vi_VN')  # Vietnamese locale

# Danh sach so thich thuc te
ALL_INTERESTS = [
    "Du lich", "The thao", "Am nhac", "Doc sach", "Yoga", "Nau an",
    "Lap trinh", "Co vua", "Phim anh", "Hoi hoa", "Ca phe", "Game",
    "Am thuc", "Chup anh", "Khieu vu", "Leo nui", "Boi loi", "Dap xe",
    "Cau long", "Quan ao", "Lam vuon", "Thu cong", "Thoi trang", "Tap gym"
]

PERSONALITIES = [
    "Huong ngoai, Hoat bat, Thich khám pha",
    "Huong noi, Tram tinh, Tu duy logic",
    "Huong ngoai, Hai huoc, Lac quan",
    "Huong noi, Nhay cam, Sang tao",
    "Huong ngoai, Nang dong, Thich phieu luu",
    "Huong noi, Chu dao, Yen binh",
    "Huong ngoai, Tu tin, Quyet doan",
    "Huong noi, Than trong, Suy ngam"
]

ZODIACS = [
    "Bach Duong", "Kim Nguu", "Song Tu", "Cu Giai",
    "Su Tu", "Xu Nu", "Thien Binh", "Thien Yet",
    "Nhan Ma", "Ma Ket", "Bao Binh", "Song Ngu"
]

def generate_vietnamese_name(gender):
    """Tao ten Viet realistic"""
    male_names = [
        "Minh", "Tuan", "Huy", "Dung", "Quan", "Long", "Nam", "Hai",
        "Khang", "Binh", "Cuong", "Thanh", "Phuc", "Dat", "Tien", "Hoang"
    ]
    female_names = [
        "Linh", "Nga", "Huong", "Mai", "Anh", "Trang", "Lan", "Phuong",
        "Thao", "Nhi", "Chi", "Vy", "Quynh", "Hoa", "Thu", "Dung"
    ]

    if gender == "Nam":
        return random.choice(male_names)
    else:
        return random.choice(female_names)

def generate_user(user_id):
    """Tao 1 user profile realistic"""
    gender = random.choice(["Nam", "Nu"])
    age = random.randint(22, 35)
    name = generate_vietnamese_name(gender)

    # Chon 3-5 so thich ngau nhien
    num_interests = random.randint(3, 5)
    interests = random.sample(ALL_INTERESTS, num_interests)

    personality = random.choice(PERSONALITIES)
    zodiac = random.choice(ZODIACS)

    # Looking for opposite gender, age range
    if gender == "Nam":
        looking_gender = "Nu"
    else:
        looking_gender = "Nam"

    age_min = max(22, age - 5)
    age_max = min(35, age + 5)

    return {
        "name": name,
        "age": age,
        "gender": gender,
        "personality": personality,
        "interests": interests,
        "zodiac": zodiac,
        "relationship_status": "Doc than",
        "looking_for": f"{looking_gender}, {age_min}-{age_max} tuoi"
    }

def generate_dataset(num_users=30):
    """Tao dataset voi num_users nguoi"""
    dataset = {}
    used_names = set()

    user_id = 1
    while len(dataset) < num_users:
        user = generate_user(user_id)

        # Tao user_id tu ten (lowercase)
        base_id = user["name"].lower()

        # Neu trung ten, them so
        user_id_str = base_id
        counter = 1
        while user_id_str in used_names:
            user_id_str = f"{base_id}{counter}"
            counter += 1

        used_names.add(user_id_str)
        dataset[user_id_str] = user
        user_id += 1

    return dataset

if __name__ == "__main__":
    print("Generating realistic dating profiles...")

    # Tao 30 users
    dataset = generate_dataset(30)

    # Luu vao JSON
    output_file = "data/users_realistic.json"

    # Tao thu muc data neu chua co
    import os
    os.makedirs("data", exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(dataset)} users")
    print(f"Saved to: {output_file}")

    # Hien thi 3 vi du
    print("\nSample profiles:")
    for i, (user_id, profile) in enumerate(list(dataset.items())[:3]):
        print(f"\n{i+1}. User ID: {user_id}")
        print(f"   Name: {profile['name']}")
        print(f"   Age: {profile['age']}, Gender: {profile['gender']}")
        print(f"   Personality: {profile['personality']}")
        print(f"   Interests: {', '.join(profile['interests'])}")
        print(f"   Zodiac: {profile['zodiac']}")

    print(f"\nTotal: {len(dataset)} realistic profiles generated!")
