import "./RouterModal.css";
import { RouterModel } from "../../shared/types";

interface Props {
  open: boolean;
  routers: RouterModel[];
  onClose: () => void;
  onSelect: (router: RouterModel) => void;
}

export const RouterModal = ({
  open,
  routers,
  onClose,
  onSelect,
}: Props) => {
  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Выбор маршрутизатора</h2>
          <button onClick={onClose}>✕</button>
        </div>

        <div className="router-grid">
          {routers.map((router) => (
            <div
              key={router.id}
              className="router-card"
              onClick={() => onSelect(router)}
            >
              <img src={router.image} alt={router.name} />

              <h3>{router.name}</h3>

              <p>{router.price.toLocaleString()} ₽</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};