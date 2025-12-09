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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
} from "recharts";

const COLORS = ["#10b981", "#3b82f6", "#ef4444", "#f59e0b", "#8b5cf6"];

const ReportsCharts = ({ candidates }: any) => {
  const pipelineData = [
    { name: "Applied", value: candidates.length * 1.6 },
    { name: "Shortlisted", value: Math.round(candidates.length * 0.6) },
    { name: "Assessed", value: candidates.filter((c:any)=>c.assessment!=null).length },
    { name: "Interviewed", value: candidates.filter((c:any)=>c.interview!=null).length },
    { name: "Recommended", value: Math.min(3, candidates.length) },
  ];

  const pieData = [
    { name: "Strong", value: candidates.filter((c:any)=>c.recommendation==='Strong').length },
    { name: "Moderate", value: candidates.filter((c:any)=>c.recommendation==='Moderate').length },
    { name: "Weak", value: candidates.filter((c:any)=>c.recommendation==='Weak').length },
  ];

  const radarData = candidates.slice(0,3).map((c:any) => ({
    subject: c.name,
    Assessment: c.assessment || 0,
    Interview: c.interview || 0,
    Resume: c.resumeMatch || 0,
  }));

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
          <h4 className="text-md font-semibold">Final Categories (pie)</h4>
          <div style={{ width: "100%", height: 160 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={30} outerRadius={60}>
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
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
