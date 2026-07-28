# BO SUNG PROMPTS CHO CUPID AGENT

## TONG QUAN

Da them **7 nhom prompts moi** vao file `src/prompts.py` de ho tro LLM hieu ro hon ve:
- Cach su dung tools dung format
- Cach phan tich tuong thich chi tiet
- Cach xu ly loi gracefully
- Cach dua ra loi khuyen ca nhan hoa

---

## 1. REACT_FEW_SHOT_EXAMPLES

**Muc dich**: Hoc LLM cach su dung tools bang vi du cu the

**Noi dung**: 4 vi du mau
- Vi du 1: Tra cuu ho so don gian
- Vi du 2: Tinh do tuong thich
- Vi du 3: Tim doi tuong phu hop
- Vi du 4: Xu ly loi khi user khong ton tai

**Cach su dung**: Chen vao REACT_SYSTEM_PROMPT de LLM hoc theo mau

---

## 2. PERSONALITY_ADVICE_TEMPLATES

**Muc dich**: Dua ra loi khuyen khac nhau tuy theo tinh cach

**Noi dung**:
```python
{
    "huong_ngoai": "Chon dia diem soi dong, the hien nhiet tinh...",
    "huong_noi": "Chon khong gian yen tinh, tro chuyen sau..."
}
```

**Cach su dung**: Agent dua vao tinh cach user de tuy chinh loi khuyen

---

## 3. COMPATIBILITY_DESCRIPTIONS

**Muc dich**: Giai thich y nghia cua diem tuong thich

**Noi dung**: 4 muc do
- `very_high` (80-100): Tiem nang rat lon
- `high` (60-79): Kha hop nhau
- `medium` (40-59): Can no luc them
- `low` (<40): Nhieu khac biet

**Cach su dung**: Sau khi tinh diem, agent giai thich y nghia va dua ra loi khuyen

---

## 4. DATE_ACTIVITY_SUGGESTIONS

**Muc dich**: Goi y hoat dong hen ho phu hop voi tinh cach

**Noi dung**: 4 loai hoat dong
- `active`: Leo nui, chay bo, bowling, the thao...
- `relaxed`: Cafe, xem phim, dao bo bai bien...
- `creative`: Ve tranh, nau an, chup anh...
- `intellectual`: Cafe sach, talk show, board game...

**Cach su dung**: Agent chon hoat dong dua tren so thich cua cap doi

---

## 5. RED_FLAGS_WARNING

**Muc dich**: Canh bao dau hieu xau trong moi quan he

**Noi dung**: 7 dau hieu canh bao
1. Thieu ton trong
2. Kiem soat qua muc
3. Thieu trung thuc
4. Bao luc (loi noi/hanh dong)
5. Thieu trach nhiem
6. Thieu no luc
7. Khong tuong thich gia tri cot loi

**Cach su dung**: Hien thi khi user hoi ve van de moi quan he

---

## 6. GREEN_FLAGS_LIST

**Muc dich**: Nhan dien dau hieu tich cuc trong moi quan he

**Noi dung**: 8 dau hieu tot
1. Ton trong
2. Giao tiep co mo
3. Tin tuong
4. Ho tro
5. Trach nhiem
6. Tuong thich gia tri
7. No luc
8. Hai huoc

**Cach su dung**: Dua ra khi phan tich tinh cach hoac tuong thich

---

## 7. USER_GOAL_PROMPTS

**Muc dich**: Tuy chinh chien luoc dua tren muc tieu user

**Noi dung**: 4 loai muc tieu
- `tim_ban_doi`: Uu tien gia tri song, muc tieu tuong lai
- `hen_ho_thu_gian`: Tap trung chemistry, trai nghiem vui
- `mo_rong_quan_he`: De xuat nhieu lua chon da dang
- `tu_van_quan_he`: Loi khuyen xay dung va duy tri

**Cach su dung**: Agent dieu chinh cach phan tich dua tren muc tieu

---

## CAI TIEN SO VOI PHIEN BAN CU

| Truoc khi bo sung | Sau khi bo sung |
|:------------------|:----------------|
| Chi co System Prompt chung | Co 7 nhom prompts chi tiet |
| Khong co vi du mau | 4 vi du cu the cho LLM hoc |
| Loi khuyen chung chung | Loi khuyen ca nhan hoa theo tinh cach |
| Chi co diem so | Co giai thich y nghia diem so |
| Khong co goi y hoat dong | 4 nhom hoat dong hen ho |
| Khong canh bao red flags | Co danh sach red/green flags |
| Khong phan biet muc tieu | Tuy chinh theo 4 loai muc tieu |

---

## VI DU SU DUNG

### Truoc khi bo sung:
```
User: "Minh va Linh co hop khong?"
Agent: "Diem tuong thich: 60/100"
```

### Sau khi bo sung:
```
User: "Minh va Linh co hop khong?"
Agent: 
"Diem tuong thich: 60/100 (CAO)

Y nghia: Hai ban kha hop nhau va co the xay dung moi quan he tot. 
Hay kham pha them nhung diem chung khac, ton trong su khac biet, 
va giao tiep co mo ve mong muon.

Goi y hoat dong hen ho:
Vi ca hai deu thich du lich va am nhac, hay thu:
- Di leo nui va nghe nhac acoustic tren dinh
- Tham du festival am nhac
- Cafe co nhac song

Dau hieu tich cuc can tim:
✓ Ton trong y kien cua nhau
✓ Giao tiep co mo ve cam xuc
✓ San sang dau tu thoi gian cho nhau"
```

---

## HUONG DAN CHO ROLE 3 (PROMPT ENGINEER)

### Cach su dung cac prompts moi:

1. **REACT_FEW_SHOT_EXAMPLES**: 
   - Chen vao cuoi REACT_SYSTEM_PROMPT
   - Giup LLM hieu ro format Thought-Action-Observation

2. **PERSONALITY_ADVICE_TEMPLATES**:
   - Dung trong Final Answer
   - Chon template dua tren tinh cach tu get_personality_profile

3. **COMPATIBILITY_DESCRIPTIONS**:
   - Sau khi calculate_compatibility
   - Map diem so voi muc do (very_high/high/medium/low)

4. **DATE_ACTIVITY_SUGGESTIONS**:
   - Ket hop voi so thich chung
   - Goi y 2-3 hoat dong cu the

5. **RED_FLAGS_WARNING / GREEN_FLAGS_LIST**:
   - Hien thi khi user hoi ve van de moi quan he
   - Khong hien thi khi chi tinh diem tuong thich don thuan

6. **USER_GOAL_PROMPTS**:
   - Neu user noi ro muc tieu, them vao System Prompt
   - Vi du: User: "Tim ban doi lau dai" -> them prompt tim_ban_doi

---

## KIEM TRA

Chay lenh nay de dam bao tat ca prompts da load:

```python
from src.prompts import (
    REACT_FEW_SHOT_EXAMPLES,
    PERSONALITY_ADVICE_TEMPLATES,
    COMPATIBILITY_DESCRIPTIONS,
    DATE_ACTIVITY_SUGGESTIONS,
    RED_FLAGS_WARNING,
    GREEN_FLAGS_LIST,
    USER_GOAL_PROMPTS
)

print("All prompts loaded successfully!")
print(f"- Few-shot examples: {len(REACT_FEW_SHOT_EXAMPLES)} chars")
print(f"- Personality templates: {len(PERSONALITY_ADVICE_TEMPLATES)} types")
print(f"- Compatibility levels: {len(COMPATIBILITY_DESCRIPTIONS)} levels")
print(f"- Activity types: {len(DATE_ACTIVITY_SUGGESTIONS)} types")
```

---

## KET LUAN

✓ Da bo sung 7 nhom prompts chi tiet
✓ Tang kha nang ca nhan hoa cua Agent
✓ Giup LLM hieu ro hon ve format va flow
✓ Cung cap loi khuyen chat luong cao hon
✓ Tang tinh thuc te va gia tri cho user

**File src/prompts.py bay gio da day du va san sang cho production!**
