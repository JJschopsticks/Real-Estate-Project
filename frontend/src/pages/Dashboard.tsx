import { useEffect, useState } from "react";
import Modal from "react-modal";

import { api } from "../services/api";

import type { Property } from "../types/Property";

import PropertyModal from "../components/PropertyModal";
import StatsCards from "../components/StatsCards";
import CityChart from "../components/CityChart";

Modal.setAppElement("#root");

export default function Dashboard() {
  const [properties, setProperties] =
    useState<Property[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [selectedProperty, setSelectedProperty] =
    useState<Property | null>(null);

  const [isModalOpen, setIsModalOpen] =
    useState(false);

  const [selectedCity, setSelectedCity] =
    useState("All");

  const [minRoi, setMinRoi] =
    useState("");

  const [minScore, setMinScore] =
    useState("");

  useEffect(() => {
    const fetchProperties = async () => {
      try {
        const response =
          await api.get("/properties");

        setProperties(response.data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchProperties();
  }, []);

  const openModal = (
    property: Property
  ) => {
    setSelectedProperty(property);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const handleRefresh = () => {
    alert(
      "Refresh pipeline not connected yet."
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <h1 className="text-3xl font-bold">
          Loading...
        </h1>
      </div>
    );
  }

  const bestRoi = Math.max(
    ...properties.map((p) => p.roi_pct)
  );

  const bestScore = Math.max(
    ...properties.map(
      (p) => p.investment_score
    )
  );

  const averageRoi =
    properties.reduce(
      (sum, p) => sum + p.roi_pct,
      0
    ) / properties.length;

  const topProperty = properties[0];

  const cities = [
    "All",
    ...new Set(
      properties.map(
        (p) => p.city
      )
    ),
  ];

  const filteredProperties =
    properties.filter((property) => {
      const cityMatch =
        selectedCity === "All" ||
        property.city === selectedCity;

      const roiMatch =
        minRoi === "" ||
        property.roi_pct >= Number(minRoi);

      const scoreMatch =
        minScore === "" ||
        property.investment_score >= Number(minScore);

      return (
        cityMatch &&
        roiMatch &&
        scoreMatch
      );
    });

  return (
    <div className="min-h-screen bg-slate-100 p-8">

      <div className="flex justify-between items-center mb-8">

        <h1 className="text-4xl font-bold">
          Real Estate Scanner
        </h1>

        <button
          onClick={handleRefresh}
          className="
            bg-slate-800
            text-white
            px-5
            py-3
            rounded-lg
            font-semibold
            shadow-md
            hover:bg-slate-900
            transition
          "
        >
          Refresh Data
        </button>

      </div>

      <StatsCards
        propertyCount={properties.length}
        bestRoi={bestRoi}
        bestScore={bestScore}
        averageRoi={averageRoi}
      />

      <div
        className="
          bg-white
          rounded-xl
          shadow
          p-4
          mb-8
          flex
          gap-4
          items-end
        "
      >

        <div>

          <label className="block text-sm mb-1">
            City
          </label>

          <select
            value={selectedCity}
            onChange={(e) =>
              setSelectedCity(
                e.target.value
              )
            }
            className="
              border
              rounded
              px-3
              py-2
            "
          >

            {cities.map((city) => (

              <option
                key={city}
                value={city}
              >
                {city}
              </option>

            ))}

          </select>

        </div>

        <div>

          <label className="block text-sm mb-1">
            Min ROI
          </label>

          <input
            type="number"
            value={minRoi}
            onChange={(e) =>
              setMinRoi(
                e.target.value
              )
            }
            className="
              border
              rounded
              px-3
              py-2
            "
          />

        </div>

        <div>

          <label className="block text-sm mb-1">
            Min Score
          </label>

          <input
            type="number"
            value={minScore}
            onChange={(e) =>
              setMinScore(
                e.target.value
              )
            }
            className="
              border
              rounded
              px-3
              py-2
            "
          />

        </div>

      </div>

      <div className="grid grid-cols-2 gap-6 mb-8">

        <div
          className="
            bg-white
            rounded-xl
            shadow-lg
            p-6
            border-l-8
            border-yellow-500
          "
        >

          <h2
            className="
              text-2xl
              font-bold
              mb-4
            "
          >
            🏆 Best Investment Opportunity
          </h2>

          <p
            className="
              text-lg
              font-semibold
              mb-4
            "
          >
            {topProperty.id.replaceAll(
              "-",
              " "
            )}
          </p>

          <div
            className="
              grid
              grid-cols-2
              gap-4
            "
          >

            <div>

              <p className="text-gray-500">
                Price
              </p>

              <p className="font-bold">
                $
                {topProperty.listing_price.toLocaleString()}
              </p>

            </div>

            <div>

              <p className="text-gray-500">
                ROI
              </p>

              <p className="font-bold text-green-600">
                {topProperty.roi_pct}%
              </p>

            </div>

            <div>

              <p className="text-gray-500">
                Appreciation
              </p>

              <p className="font-bold">
                {topProperty.five_year_appreciation_pct}%
              </p>

            </div>

            <div>

              <p className="text-gray-500">
                Score
              </p>

              <p className="font-bold text-blue-700">
                {topProperty.investment_score}
              </p>

            </div>

          </div>

        </div>

        <CityChart
          properties={filteredProperties}
        />

      </div>

      <h3 className="text-xl mb-2">
        Showing Top 10 of {filteredProperties.length}
        Matching Properties
      </h3>

      <h2 className="text-2xl font-semibold mb-4">
        Property Rankings
      </h2>

      <div
        className="
          bg-white
          rounded-xl
          shadow-lg
          overflow-x-auto
        "
      >

        <table className="w-full">

          <thead className="bg-slate-800 text-white">

            <tr>

              <th className="px-4 py-3 text-left">
                Rank
              </th>

              <th className="px-4 py-3 text-left">
                Address
              </th>

              <th className="px-4 py-3 text-left">
                City
              </th>

              <th className="px-4 py-3 text-left">
                Price
              </th>

              <th className="px-4 py-3 text-left">
                Rent
              </th>

              <th className="px-4 py-3 text-left">
                ROI
              </th>

              <th className="px-4 py-3 text-left">
                5-Yr App.
              </th>

              <th className="px-4 py-3 text-left">
                Score
              </th>

              <th className="px-4 py-3 text-left">
                Details
              </th>

            </tr>

          </thead>

          <tbody>

            {filteredProperties
              .slice(0, 10)
              .map((property) => (

                <tr
                  key={property.rank}
                  className="
                    border-b
                    hover:bg-slate-50
                  "
                >

                  <td className="px-4 py-3">
                    {property.rank}
                  </td>

                  <td className="px-4 py-3">
                    {property.id.replaceAll("-", " ")}
                  </td>

                  <td className="px-4 py-3">
                    {property.city}
                  </td>

                  <td className="px-4 py-3">
                    ${property.listing_price.toLocaleString()}
                  </td>

                  <td className="px-4 py-3">
                    ${property.estimated_rent.toLocaleString()}
                  </td>

                  <td
                    className={`px-4 py-3 font-semibold ${
                      property.roi_pct >= 0
                        ? "text-green-600"
                        : "text-red-600"
                    }`}
                  >
                    {property.roi_pct}%
                  </td>

                  <td className="px-4 py-3">
                    {property.five_year_appreciation_pct}%
                  </td>

                  <td className="px-4 py-3 font-bold text-blue-700">
                    {property.investment_score}
                  </td>

                  <td className="px-4 py-3">

                    <button
                      onClick={() =>
                        openModal(property)
                      }
                      className="
                        bg-blue-600
                        text-white
                        px-3
                        py-2
                        rounded-lg
                        hover:bg-blue-700
                        transition
                      "
                    >
                      View
                    </button>

                  </td>

                </tr>

              ))}

          </tbody>

        </table>

      </div>

      <PropertyModal
        property={selectedProperty}
        isOpen={isModalOpen}
        onClose={closeModal}
      />

    </div>
  );
}