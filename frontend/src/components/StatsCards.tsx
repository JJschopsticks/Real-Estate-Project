interface StatsCardsProps {
  propertyCount: number;
  bestRoi: number;
  bestScore: number;
  averageRoi: number;
}

export default function StatsCards({
  propertyCount,
  bestRoi,
  bestScore,
  averageRoi,
}: StatsCardsProps) {

  return (

    <div className="grid grid-cols-4 gap-4 mb-8">

      <div className="bg-white rounded-xl shadow p-4">

        <p className="text-sm text-gray-500">
          Properties
        </p>

        <h2 className="text-3xl font-bold">
          {propertyCount}
        </h2>

      </div>

      <div className="bg-white rounded-xl shadow p-4">

        <p className="text-sm text-gray-500">
          Best ROI
        </p>

        <h2 className="text-3xl font-bold">
          {bestRoi.toFixed(2)}%
        </h2>

      </div>

      <div className="bg-white rounded-xl shadow p-4">

        <p className="text-sm text-gray-500">
          Best Score
        </p>

        <h2 className="text-3xl font-bold">
          {bestScore.toFixed(2)}
        </h2>

      </div>

      <div className="bg-white rounded-xl shadow p-4">

        <p className="text-sm text-gray-500">
          Average ROI
        </p>

        <h2 className="text-3xl font-bold">
          {averageRoi.toFixed(2)}%
        </h2>

      </div>

    </div>

  );
}