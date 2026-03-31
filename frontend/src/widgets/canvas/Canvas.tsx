import "./Canvas.css";
import { Device, Link, Room, Wall } from "../../shared/types";
import { useState, useRef } from "react";

interface Props {
  devices: Device[];
  links: Link[];
  rooms: Room[];
  walls: Wall[];
  onMoveDevice: (id: number, x: number, y: number) => void;
  onCreateLink: (fromId: number, toId: number) => void;
  drawingWall: boolean;
  addWall: (wall: Wall) => void;
}

export const Canvas = ({
  devices,
  links,
  rooms,
  walls,
  onMoveDevice,
  onCreateLink,
  drawingWall,
  addWall,
}: Props) => {
  const canvasRef = useRef<HTMLDivElement>(null);

  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [linkDrag, setLinkDrag] = useState<{ fromId: number; x: number; y: number } | null>(null);
  const [wallDrag, setWallDrag] = useState<{ x1: number; y1: number; x2: number; y2: number } | null>(null);

  // Преобразуем координаты мыши в координаты Canvas
  const getCanvasCoords = (e: React.MouseEvent) => {
    const rect = canvasRef.current!.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  };

  const handleMouseDownDevice = (e: React.MouseEvent, device: Device) => {
    if (drawingWall) return;
    const { x, y } = getCanvasCoords(e);
    setDraggingId(device.id);
    setOffset({ x: x - device.x, y: y - device.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    const { x, y } = getCanvasCoords(e);

    if (draggingId !== null) {
      onMoveDevice(draggingId, x - offset.x, y - offset.y);
    }

    if (linkDrag) {
      setLinkDrag({ ...linkDrag, x, y });
    }

    if (wallDrag) {
      setWallDrag({ ...wallDrag, x2: x, y2: y });
    }
  };

  const handleMouseUp = (e: React.MouseEvent) => {
    const { x, y } = getCanvasCoords(e);

    if (linkDrag) {
      const target = devices.find(
        (d) => x >= d.x && x <= d.x + 100 && y >= d.y && y <= d.y + 40
      );
      if (target && target.id !== linkDrag.fromId) {
        onCreateLink(linkDrag.fromId, target.id);
      }
      setLinkDrag(null);
    }

    if (wallDrag) {
      addWall({ id: Date.now(), ...wallDrag });
      setWallDrag(null);
    }

    setDraggingId(null);
  };

  const handleDeviceClick = (device: Device) => {
    if (!drawingWall) setLinkDrag({ fromId: device.id, x: device.x + 50, y: device.y + 20 });
  };

  const handleMouseDownCanvas = (e: React.MouseEvent) => {
    if (drawingWall) {
      const { x, y } = getCanvasCoords(e);
      setWallDrag({ x1: x, y1: y, x2: x, y2: y });
    }
  };

  return (
    <div
      ref={canvasRef}
      className="canvas"
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseDown={handleMouseDownCanvas}
    >
      {/* Комнаты */}
      {rooms.map((room) => (
        <div
          key={room.id}
          style={{
            position: "absolute",
            top: room.y,
            left: room.x,
            width: room.width,
            height: room.height,
            border: "2px solid black",
            backgroundColor: "#fff8",
            zIndex: 1,
          }}
        />
      ))}

      {/* Стены */}
      <svg
        className="walls"
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
          zIndex: 2,
        }}
      >
        {walls.map((w) => (
          <line
            key={w.id}
            x1={w.x1}
            y1={w.y1}
            x2={w.x2}
            y2={w.y2}
            stroke="black"
            strokeWidth={2}
          />
        ))}
        {wallDrag && (
          <line
            x1={wallDrag.x1}
            y1={wallDrag.y1}
            x2={wallDrag.x2}
            y2={wallDrag.y2}
            stroke="gray"
            strokeWidth={2}
            strokeDasharray="4"
          />
        )}
      </svg>

      {/* Линии между устройствами */}
      <svg
        className="links"
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
          zIndex: 3,
        }}
      >
        {links.map((l) => {
          const from = devices.find((d) => d.id === l.fromId);
          const to = devices.find((d) => d.id === l.toId);
          if (!from || !to) return null;
          return (
            <line
              key={l.id}
              x1={from.x + 50}
              y1={from.y + 20}
              x2={to.x + 50}
              y2={to.y + 20}
              stroke="black"
              strokeWidth={2}
            />
          );
        })}
        {linkDrag && (
          <line
            x1={devices.find((d) => d.id === linkDrag.fromId)!.x + 50}
            y1={devices.find((d) => d.id === linkDrag.fromId)!.y + 20}
            x2={linkDrag.x}
            y2={linkDrag.y}
            stroke="gray"
            strokeWidth={2}
            strokeDasharray="4"
          />
        )}
      </svg>

      {/* Устройства */}
      {devices.map((d) => (
        <div
          key={d.id}
          className="device"
          style={{ top: d.y, left: d.x, zIndex: 4 }}
          onMouseDown={(e) => handleMouseDownDevice(e, d)}
          onClick={() => handleDeviceClick(d)}
        >
          {d.type}
        </div>
      ))}
    </div>
  );
};