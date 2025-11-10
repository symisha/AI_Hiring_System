import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  Settings,
  HelpCircle,
  LogOut,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import DashboardTopbar from "@/components/DashboardTopbar";

const Dashboard = () => {
  const stats = [
    {
      title: "Total Jobs Posted",
      value: "12",
      icon: Briefcase,
      gradient: "from-blue-600 to-blue-400",
    },
    {
      title: "Total Recruited",
      value: "48",
      icon: Users,
      gradient: "from-purple-600 to-purple-400",
    },
    {
      title: "Active Jobs",
      value: "5",
      icon: LayoutDashboard,
      gradient: "from-pink-600 to-pink-400",
    },
  ];

  const activeJobs = [
    { id: 1, title: "Senior Frontend Developer" },
    { id: 2, title: "DevOps Engineer" },
    { id: 3, title: "UI/UX Designer" },
    { id: 4, title: "Product Manager" },
    { id: 5, title: "Software Engineer" },
  ];

  const jobOptions = [
    { title: "Resume Screening", path: "/screening" },
    { title: "Assessments", path: "/assessments" },
    { title: "AI Interviews", path: "/interviews" },
    { title: "Reports", path: "/reports" },
  ];

  const generalOptions = [
    { title: "Settings", icon: Settings, path: "/settings" },
    { title: "Help", icon: HelpCircle, path: "/help" },
    { title: "Logout", icon: LogOut, path: "/logout" },
  ];

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="w-80 p-4">
        <div className="h-full rounded-3xl bg-card p-4 shadow-sm ">
          {/* Logo */}
          <div className="flex items-center gap-2 mb-6">
            <img
              src="/src/assets/logo-purple.svg"
              alt="AI Hiring"
              className="h-8 w-8"
            />
            <span className="font-bold text-xl bg-gradient-primary bg-clip-text text-transparent">
              AI Hiring
            </span>
          </div>

          <Separator className="my-2" />

          {/* Active Jobs Section */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              ACTIVE JOBS
            </h3>
            <ScrollArea className="h-[200px]">
              {activeJobs.map((job) => (
                <div key={job.id} className="group">
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-left mb-1 px-2 hover:bg-secondary"
                  >
                    {job.title}
                  </Button>

                  <div className="hidden group-hover:block pl-4 space-y-1">
                    {jobOptions.map((option) => (
                      <Button
                        key={option.title}
                        variant="ghost"
                        size="sm"
                        className="w-full justify-start text-sm text-muted-foreground hover:text-primary hover:bg-secondary/80"
                      >
                        {option.title}
                      </Button>
                    ))}
                  </div>
                </div>
              ))}
            </ScrollArea>
          </div>

          {/* General Section */}
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">GENERAL</h3>
            {generalOptions.map((option) => (
              <Button
                key={option.title}
                variant="ghost"
                className="w-full justify-start mb-1 hover:bg-secondary hover:text-primary"
              >
                <option.icon className="mr-2 h-4 w-4" />
                {option.title}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6 overflow-y-auto">
        {/* Top Bar (Search, Profile, etc.) */}
        <DashboardTopbar />

        {/* Welcome Message */}
        <h1 className="text-3xl font-bold mb-2">Welcome back, HR Manager</h1>
        <p className="text-muted-foreground mb-8">
          Here's what's happening with your recruitment pipeline.
        </p>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {stats.map((stat) => (
            <Card key={stat.title} className="relative overflow-hidden">
              <div
                className={`absolute inset-0 opacity-10 bg-gradient-to-br ${stat.gradient}`}
              />
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <stat.icon
                  className={`h-5 w-5 bg-gradient-to-br ${stat.gradient} bg-clip-text text-transparent`}
                />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recent Activity */}
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 opacity-5 bg-gradient-to-br from-purple-600 to-blue-600" />
          <CardHeader>
            <CardTitle className="text-xl">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="h-2 w-2 rounded-full bg-green-500" />
                <p className="text-sm">
                  <span className="font-medium">Senior Frontend Developer</span>
                  <span className="text-muted-foreground">
                    {" "}
                    - New candidate applied 2 hours ago
                  </span>
                </p>
              </div>
              <div className="flex items-center gap-4">
                <div className="h-2 w-2 rounded-full bg-blue-500" />
                <p className="text-sm">
                  <span className="font-medium">DevOps Engineer</span>
                  <span className="text-muted-foreground">
                    {" "}
                    - Interview scheduled for tomorrow
                  </span>
                </p>
              </div>
              <div className="flex items-center gap-4">
                <div className="h-2 w-2 rounded-full bg-purple-500" />
                <p className="text-sm">
                  <span className="font-medium">UI/UX Designer</span>
                  <span className="text-muted-foreground">
                    {" "}
                    - Assessment completed by 3 candidates
                  </span>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
