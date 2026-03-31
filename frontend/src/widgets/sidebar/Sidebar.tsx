import { DeviceType } from "../../shared/types";
import './Sidebar.css'

interface Props {
  onAddDevice: (type: DeviceType) => void;
  onAddRoom: (width: number, height: number) => void;
  onStartWallDraw: () => void;
}

export const Sidebar = ({ onAddDevice, onAddRoom, onStartWallDraw }: Props) => {
  return (
    <aside style={{ width: 150, borderRight: "1px solid black", padding: 10 }}>
      <h3>Устройства</h3>
      <div>
        <button onClick={() => onAddDevice("ПК")}>🖥 ПК</button>
      </div>
      <div>
        <button onClick={() => onAddDevice("Маршрутизатор")}>📡 Маршрутизатор</button>
      </div>
      <div>
        <button onClick={() => onAddDevice("Коммутатор")}>🔀 Коммутатор</button>
      </div>

      <div style={{ marginTop: 20 }}>
        <h3>Помещение</h3>
        <button
          onClick={() => {
            const width = parseInt(prompt("Ширина помещения (м):", "10") || "10", 10);
            const height = parseInt(prompt("Длина помещения (м):", "8") || "8", 10);
            onAddRoom(width * 50, height * 50);
          }}
        >
          Добавить помещение
        </button>
      </div>

      <div style={{ marginTop: 10 }}>
        <h3>Стены</h3>
        <button onClick={() => onStartWallDraw()}>Начать рисовать стену</button>
      </div>
    </aside>
  );
};