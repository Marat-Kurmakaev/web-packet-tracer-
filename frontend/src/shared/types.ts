export type DeviceType = "ПК" | "Маршрутизатор" | "Коммутатор";

export interface RouterModel {
  id: number;
  name: string;
  image: string;
  price: number;
}

export interface Device {
  id: number;
  type: DeviceType;
  x: number;
  y: number;
  цена: number;

  // для роутеров
  model?: RouterModel;
}

export interface Link {
  id: number;
  fromId: number;
  toId: number;
  цена: number;
}

export interface Room {
  id: number;
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Wall {
  id: number;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}