from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date

app = FastAPI()

rooms = [
    {"id": 1, "code": "R101", "name": "Room 101",
        "capacity": 30, "status": "AVAILABLE"},
    {"id": 2, "code": "R102", "name": "Room 102",
        "capacity": 20, "status": "AVAILABLE"},
    {"id": 3, "code": "R103", "name": "Room 103",
        "capacity": 40, "status": "MAINTENANCE"}
]
room_bookings = [
    {
        "id": 1,
        "room_id": 1,
        "class_name": "Python Basic",
        "student_count": 25,
        "date": "2026-07-01",
        "slot": "MORNING"
    }
]


class Rooms(BaseModel):
    code: str = Field(min_length=1)
    name: str = Field(min_length=1)
    capacity: int = Field(gt=0)
    status: Literal["AVAILABLE", "IN_USE", "MAINTENANCE"]


class Bookings(BaseModel):
    room_id: int
    class_name: str = Field(min_length=1)
    student_count: int = Field(gt=0)
    date: date
    slot: Literal["MORNING", "AFTERNOON", "EVENING"]


@app.post("/rooms", status_code=201)
def create_rooms(new_room: Rooms):
    if new_room.name.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Tên phòng không được để trống"
        )

    for room in rooms:
        if room["code"] == new_room.code:
            raise HTTPException(
                status_code=400,
                detail="Mã phòng đã tồn tại"
            )

    new_id = max((room["id"] for room in rooms), default=0) + 1

    rooms.append({
        "id": new_id,
        "code": new_room.code,
        "name": new_room.name,
        "capacity": new_room.capacity,
        "status": new_room.status
    })

    return {
        "message": "Thêm phòng mới thành công"
    }


@app.get("/rooms")
def get_rooms(keyword: str | None = None, status: str | None = None, min_capacity: int | None = None):
    if not rooms:
        return {"message": "Danh sách phòng đang trống"}

    result = rooms
    if keyword:
        result = [room for room in result if keyword.lower(
        ) in room["code"].lower() or keyword.lower() in room["name"].lower()]
    if status:
        result = [room for room in result if room["status"] == status]
    if min_capacity:
        result = [room for room in result if room["capacity"] >= min_capacity]

    if not result:
        return {"message": "Không tìm thấy phòng"}
    return result


@app.get("/rooms/{room_id}")
def get_room(room_id: int):
    if not rooms:
        return {"message": "Dannh sách lịch đang trống"}

    for room in rooms:
        if room["id"] == room_id:
            return room

    raise HTTPException(
        status_code=404,
        detail="Room not found."
    )


@app.put("/rooms/{room_id}")
def update_room(room_id: int, new_info: Rooms):
    if not rooms:
        return {"message": "Dannh sách lịch đang trống"}

    if new_info.name.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Tên phòng không được để trống"
        )
    
    for room in rooms:
        if room["id"] == room_id:
            room["code"] = new_info.code
            room["name"] = new_info.name
            room["capacity"] = new_info.capacity
            room["status"] = new_info.status

            return {"message": f"Cập nhật phòng {room_id} thành công"}

    raise HTTPException(
        status_code=404,
        detail="Room not found."
    )


@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    if not rooms:
        return {"message": "Dannh sách lịch đang trống"}

    for index, room in enumerate(rooms):
        if room["id"] == room_id:
            rooms.pop(index)
            return {"message": f"Xóa phòng {room_id} thành công"}

    raise HTTPException(
        status_code=404,
        detail="Room not found."
    )


@app.post("/room-bookings", status_code=201)
def create_bookings(new_booking: Bookings):
    found = None
    for room in rooms:
        if room["id"] == new_booking.room_id:
            found = room
            break

    if not found:
        raise HTTPException(
            status_code=404,
            detail="Room not found."
        )

    if found["status"] != "AVAILABLE":
        raise HTTPException(
            status_code=400,
            detail="Room is not available"
        )

    if new_booking.student_count > found["capacity"]:
        raise HTTPException(
            status_code=400,
            detail="Phòng không đủ chỗ"
        )

    for booking in room_bookings:
        if booking["room_id"] == new_booking.room_id and booking["date"] == str(new_booking.date) and booking["slot"] == new_booking.slot:
            raise HTTPException(
                status_code=400,
                detail="Phòng đã được đặt"
            )

    new_id = max((booking["id"] for booking in room_bookings), default=0) + 1
    room_bookings.append({
        "id": new_id,
        "room_id": new_booking.room_id,
        "class_name": new_booking.class_name,
        "student_count": new_booking.student_count,
        "date": str(new_booking.date),
        "slot": new_booking.slot
    })
    return {"message": "Đặt phòng thành công"}


@app.get("/room-bookings")
def get_bookings():
    if not room_bookings:
        return {"message": "Danh sách lịch đang trống"}
    return room_bookings
