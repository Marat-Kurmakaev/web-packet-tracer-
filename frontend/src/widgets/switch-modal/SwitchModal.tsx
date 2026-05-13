import "./SwitchModal.css";
import { RouterModel } from "../../shared/types";

interface Props {
  open: boolean;
  switches: RouterModel[];
  onClose: () => void;
  onSelect: (router: RouterModel) => void;
}

export const SwitchModal = ({
  open,
  switches,
  onClose,
  onSelect,
}: Props) => {
  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Выбор коммутатора</h2>
          <button onClick={onClose}>✕</button>
        </div>

        <div className="router-grid">
          {switches.map((sw) => (
            <div
              key={sw.id}
              className="router-card"
              onClick={() => onSelect(sw)}
            >
              <img src={sw.image} alt={sw.name} />

              <h3>{sw.name}</h3>

              <p>{sw.price.toLocaleString()} ₽</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};