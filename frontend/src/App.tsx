import { useState } from "react";
import { Sidebar } from "./widgets/sidebar/Sidebar";
import { Canvas } from "./widgets/canvas/Canvas";
import { Device, DeviceType, Link, Room, Wall } from "./shared/types";

export default function App() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [links, setLinks] = useState<Link[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [walls, setWalls] = useState<Wall[]>([]);
  const [drawingWall, setDrawingWall] = useState(false);

  const addDevice = (type: DeviceType) => {
    setDevices((prev) => [...prev, { id: Date.now(), type, x: 200, y: 150, цена: 1000 }]);
  };

  const moveDevice = (id: number, x: number, y: number) => {
    setDevices((prev) => prev.map((d) => (d.id === id ? { ...d, x, y } : d)));
  };

  const createLink = (fromId: number, toId: number) => {
    if (links.some((l) => (l.fromId === fromId && l.toId === toId) || (l.fromId === toId && l.toId === fromId))) return;
    setLinks((prev) => [...prev, { id: Date.now(), fromId, toId, цена: 100 }]);
  };

  const addRoom = (width: number, height: number) => {
    setRooms((prev) => [...prev, { id: Date.now(), x: 100, y: 100, width, height }]);
  };

  const startWallDraw = () => setDrawingWall(true);
  const addWall = (wall: Wall) => {
    setWalls((prev) => [...prev, wall]);
    setDrawingWall(false);
  };

  const total =
    devices.reduce((sum, d) => sum + d.цена, 0) + links.reduce((sum, l) => sum + l.цена, 0);

  return (
    <div className="app" style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <header style={{ padding: 10, borderBottom: "1px solid black" }}>
        Конструктор сети — 💰 {total} ₽
      </header>
      <div style={{ display: "flex", flex: 1 }}>
        <Sidebar onAddDevice={addDevice} onAddRoom={addRoom} onStartWallDraw={startWallDraw} />
        <Canvas
          devices={devices}
          links={links}
          rooms={rooms}
          walls={walls}
          onMoveDevice={moveDevice}
          onCreateLink={createLink}
          drawingWall={drawingWall}
          addWall={addWall}
        />
      </div>
    </div>
  );
}