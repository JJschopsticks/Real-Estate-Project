import Modal from "react-modal";
import type { Property } from "../types/Property";

interface PropertyModalProps {
  property: Property | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function PropertyModal({
  property,
  isOpen,
  onClose,
}: PropertyModalProps) {
  if (!property) return null;

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onClose}
      contentLabel="Property Details"
      className="
        max-w-4xl
        mx-auto
        mt-10
        bg-white
        rounded-2xl
        p-8
        shadow-2xl
        relative
        max-h-[90vh]
        overflow-y-auto
      "
      overlayClassName="
        fixed
        inset-0
        bg-black/50
        flex
        justify-center
        items-start
      "
    >
      {/* Close Button */}

      <button
        onClick={onClose}
        className="
          absolute
          top-4
          right-4
          bg-red-500
          text-white
          px-3
          py-2
          rounded-lg
          font-bold
          hover:bg-red-600
          transition
        "
      >
        ✕
      </button>

      {/* Property Header */}

      <div
        className="
          bg-slate-800
          text-white
          rounded-xl
          p-5
          mb-6
        "
      >
        <h2 className="text-2xl font-bold">
          {property.id.replaceAll("-", " ")}
        </h2>

        <p className="text-slate-300 mt-1">
          Rank #{property.rank}
        </p>
      </div>

      {/* Property Details */}

      <div
        className="
          bg-slate-50
          border
          rounded-xl
          p-5
          mb-5
        "
      >
        <h3
          className="
            text-xl
            font-bold
            uppercase
            text-slate-800
            border-b
            pb-2
            mb-4
          "
        >
          Property Details
        </h3>

        <div className="space-y-2">

          <p>
            <span className="font-semibold">
              Square Feet:
            </span>{" "}
            {property.square_feet}
          </p>

          <p>
            <span className="font-semibold">
              Bedrooms:
            </span>{" "}
            {property.bedrooms}
          </p>

          <p>
            <span className="font-semibold">
              Bathrooms:
            </span>{" "}
            {property.bathrooms}
          </p>

          <p>
            <span className="font-semibold">
              Year Built:
            </span>{" "}
            {property.year_built}
          </p>

          <p>
            <span className="font-semibold">
              HOA Fee:
            </span>{" "}
            ${property.hoa_fee}
          </p>

        </div>
      </div>

      {/* Investment Metrics */}

      <div
        className="
          bg-slate-50
          border
          rounded-xl
          p-5
          mb-5
        "
      >
        <h3
          className="
            text-xl
            font-bold
            uppercase
            text-slate-800
            border-b
            pb-2
            mb-4
          "
        >
          Investment Metrics
        </h3>

        <div className="space-y-2">

          <p>
            <span className="font-semibold">
              ROI:
            </span>{" "}
            {property.roi_pct}%
          </p>

          <p>
            <span className="font-semibold">
              Estimated Rent:
            </span>{" "}
            ${property.estimated_rent.toLocaleString()}
          </p>

          <p>
            <span className="font-semibold">
              Appreciation:
            </span>{" "}
            {property.five_year_appreciation_pct}%
          </p>

          <p>
            <span className="font-semibold">
              Investment Score:
            </span>{" "}
            {property.investment_score}
          </p>

        </div>
      </div>

      {/* Neighborhood Metrics */}

      <div
        className="
          bg-slate-50
          border
          rounded-xl
          p-5
        "
      >
        <h3
          className="
            text-xl
            font-bold
            uppercase
            text-slate-800
            border-b
            pb-2
            mb-4
          "
        >
          Neighborhood Metrics
        </h3>

        <div className="space-y-2">

          <p>
            <span className="font-semibold">
              Median Income:
            </span>{" "}
            ${property.median_income?.toLocaleString()}
          </p>

          <p>
            <span className="font-semibold">
              Bachelor's %:
            </span>{" "}
            {property.bachelors_pct}
          </p>

          <p>
            <span className="font-semibold">
              Median Home Value:
            </span>{" "}
            ${property.median_home_value?.toLocaleString()}
          </p>

          <p>
            <span className="font-semibold">
              Owner Occupied %:
            </span>{" "}
            {property.owner_occupied_pct}
          </p>

        </div>
      </div>

    </Modal>
  );
}