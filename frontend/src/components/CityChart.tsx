import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

import type { Property } from "../types/Property";

interface Props {
  properties: Property[];
}

export default function CityChart({
  properties,
}: Props) {

  const data =
    properties
      .sort((a, b) => a.rank - b.rank)
      .map((property) => ({
        rank: property.rank,
        roi: property.roi_pct,
      }));

  return (

    <div
      className="
        bg-white
        rounded-xl
        shadow-lg
        p-6
        h-full
      "
    >

      <h2
        className="
          text-2xl
          font-bold
          mb-4
        "
      >
        ROI by Rank
      </h2>

      <p
        className="
          text-gray-500
          mb-4
        "
      >
        Shows how investment quality
        changes throughout the rankings.
      </p>

      <ResponsiveContainer
        width="100%"
        height={300}
      >

        <LineChart data={data}>

          <CartesianGrid
            strokeDasharray="3 3"
          />

          <XAxis
            dataKey="rank"
          />

          <YAxis />

          <Tooltip />

          <Line
            type="monotone"
            dataKey="roi"
            stroke="#1e293b"
            strokeWidth={3}
            dot={false}
          />

        </LineChart>

      </ResponsiveContainer>

    </div>

  );
}