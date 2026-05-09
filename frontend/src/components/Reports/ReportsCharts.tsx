import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const PIE_COLORS = ["#10b981", "#ef4444"];

const ReportsCharts = ({ candidates, rejectedCount = 0 }: any) => {
  const shortlistedCount = candidates.filter((c: any) => c.isShortlisted).length;

  const pipelineData = [
    { name: "Graded", value: candidates.length },
    { name: "Shortlisted", value: shortlistedCount },
    { name: "Rejected", value: rejectedCount },
  ];
  const pieData = [
    { name: "Shortlisted (≥80)", value: shortlistedCount },
    { name: "Rejected", value: rejectedCount },
  ].filter((d) => d.value > 0);

  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-md font-semibold">Pipeline (bar)</h4>
        <div style={{ width: "100%", height: 180 }}>
          <ResponsiveContainer>
            <BarChart data={pipelineData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        <div>
          <h4 className="text-md font-semibold">Shortlisted vs Rejected (pie)</h4>
          <div style={{ width: "100%", height: 180 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={35} outerRadius={65} label={({ name, value }) => `${value}`}>
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: any, name: any) => [value, name]} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* <div>
          <h4 className="text-md font-semibold">Top Candidates by Dimensions (radar)</h4>
          <div style={{ width: "100%", height: 220 }}>
            <ResponsiveContainer>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis />
                <Radar name="Assessment" dataKey="Assessment" stroke="#8884d8" fill="#8884d8" fillOpacity={0.2} />
                <Radar name="Interview" dataKey="Interview" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.2} />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div> */}
      </div>
    </div>
  );
};

export default ReportsCharts;
