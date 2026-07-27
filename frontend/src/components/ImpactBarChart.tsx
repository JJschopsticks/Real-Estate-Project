import { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
} from "recharts";

import type { Property } from "../types/Property";

export interface ImpactBin {
  label: string;
  min: number;
  max: number;
}

interface Props {
  title: string;
  description: string;
  properties: Property[];
  field: keyof Property;
  bins: ImpactBin[];
  valueFormat?: (value: number) => string;
}

interface BinDatum {
  label: string;
  avgRoi: number;
  count: number;
}

const POSITIVE_COLOR = "#2a78d6";
const NEGATIVE_COLOR = "#e34948";

interface BarShapeProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  payload?: BinDatum;
}

// Recharts hands custom Bar shapes the raw rect geometry, which can
// have a negative height (and an x/y anchored at the bar's tip rather
// than its top-left) for a below-baseline value — its own default
// Rectangle shape normalizes this internally, so a custom shape must
// do the same before drawing.
const normalizeRect = (
  x: number,
  y: number,
  width: number,
  height: number
) => {
  let nx = x;
  let ny = y;
  let nw = width;
  let nh = height;

  if (nh < 0) {
    ny += nh;
    nh = -nh;
  }

  if (nw < 0) {
    nx += nw;
    nw = -nw;
  }

  return { x: nx, y: ny, width: nw, height: nh };
};

// The "far end" (the end that carries the 4px rounded corner, per the
// dataviz mark spec) is the top edge for a positive bar and the
// bottom edge for a negative one — the baseline edge stays square
// either way.
const RoundedBar = (props: BarShapeProps) => {
  const isPositive = (props.payload?.avgRoi ?? 0) >= 0;
  const { x, y, width, height } = normalizeRect(
    props.x ?? 0,
    props.y ?? 0,
    props.width ?? 0,
    props.height ?? 0
  );
  const fill = isPositive ? POSITIVE_COLOR : NEGATIVE_COLOR;
  const r = Math.min(4, height, width / 2);

  const path = isPositive
    ? `M${x},${y + r}
       Q${x},${y} ${x + r},${y}
       L${x + width - r},${y}
       Q${x + width},${y} ${x + width},${y + r}
       L${x + width},${y + height}
       L${x},${y + height}
       Z`
    : `M${x},${y}
       L${x + width},${y}
       L${x + width},${y + height - r}
       Q${x + width},${y + height} ${x + width - r},${y + height}
       L${x + r},${y + height}
       Q${x},${y + height} ${x},${y + height - r}
       Z`;

  return <path d={path} fill={fill} />;
};

interface LabelProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  value?: number;
}

const RoiTipLabel = (props: LabelProps) => {
  const value = props.value ?? 0;
  const isPositive = value >= 0;
  const { x, y, width, height } = normalizeRect(
    props.x ?? 0,
    props.y ?? 0,
    props.width ?? 0,
    props.height ?? 0
  );
  const labelY = isPositive ? y - 6 : y + height + 14;

  return (
    <text
      x={x + width / 2}
      y={labelY}
      textAnchor="middle"
      fontSize={12}
      fontWeight={600}
      fill="#52514e"
    >
      {value > 0 ? "+" : ""}
      {value.toFixed(1)}%
    </text>
  );
};

interface BarTooltipProps {
  active?: boolean;
  payload?: { payload: BinDatum }[];
}

const BarTooltip = ({ active, payload }: BarTooltipProps) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const point = payload[0].payload;

  return (
    <div
      className="
        bg-white
        border
        border-slate-200
        rounded-lg
        shadow-lg
        px-3
        py-2
      "
    >
      <p className="text-xs text-slate-500 mb-1">{point.label}</p>

      <p className="text-sm">
        <span className="font-semibold text-slate-900">
          {point.avgRoi > 0 ? "+" : ""}
          {point.avgRoi.toFixed(2)}%
        </span>{" "}
        <span className="text-slate-500">avg. ROI</span>
      </p>

      <p className="text-xs text-slate-400">
        {point.count} properties
      </p>
    </div>
  );
};

export default function ImpactBarChart({
  title,
  description,
  properties,
  field,
  bins,
}: Props) {
  const data = useMemo<BinDatum[]>(() => {
    return bins
      .map((bin) => {
        const matches = properties.filter((property) => {
          const value = property[field] as number;
          return value >= bin.min && value < bin.max;
        });

        const avgRoi =
          matches.length === 0
            ? 0
            : matches.reduce((sum, p) => sum + p.roi_pct, 0) /
              matches.length;

        return {
          label: bin.label,
          avgRoi,
          count: matches.length,
        };
      })
      .filter((bin) => bin.count > 0);
  }, [properties, field, bins]);

  // A bar's length is only an honest magnitude cue when it grows from
  // a real zero baseline — letting the axis auto-fit tightly around
  // the (here, all-negative) values would truncate that baseline and
  // exaggerate differences between bars.
  const yDomain = useMemo<[number, number]>(() => {
    const values = data.map((d) => d.avgRoi);
    const min = Math.min(0, ...values);
    const max = Math.max(0, ...values);
    const niceFloor = Math.floor(min / 5) * 5;
    const niceCeil = Math.ceil(max / 5) * 5;

    return [niceFloor, niceCeil];
  }, [data]);

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
      <h2 className="text-2xl font-bold">{title}</h2>

      <p className="text-gray-500 mb-4">{description}</p>

      <ResponsiveContainer width="100%" height={340}>
        <BarChart
          data={data}
          margin={{ top: 24, right: 16, bottom: 8, left: 8 }}
        >
          <CartesianGrid stroke="#e1e0d9" vertical={false} />

          <XAxis
            dataKey="label"
            tick={{ fill: "#898781", fontSize: 12 }}
            stroke="#c3c2b7"
          />

          <YAxis
            domain={yDomain}
            tick={{ fill: "#898781", fontSize: 12 }}
            stroke="#c3c2b7"
            tickFormatter={(value: number) => `${value}%`}
          />

          <ReferenceLine y={0} stroke="#c3c2b7" />

          <Tooltip
            cursor={{ fill: "#f9f9f7" }}
            content={<BarTooltip />}
          />

          <Bar
            dataKey="avgRoi"
            shape={<RoundedBar />}
            barSize={24}
            label={<RoiTipLabel />}
            isAnimationActive={false}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
