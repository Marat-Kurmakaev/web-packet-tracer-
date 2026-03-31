export type DeviceType = "ПК" | "Маршрутизатор" | "Коммутатор";

export interface Device {
  id: number;
  type: DeviceType;
  x: number;
  y: number;
  цена: number; // рубли
}

export interface Link {
  id: number;
  fromId: number;
  toId: number;
  цена: number; // рубли
}

export interface Room {
  id: number;
  width: number;   // в пикселях
  height: number;  // в пикселях
  x: number;
  y: number;
}

export interface Wall {
  id: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}