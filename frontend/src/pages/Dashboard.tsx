import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import ResumeScreening from "./ResumeScreening";
import Assessments from "./Assessments";
import AIInterviews from "./AIInterviews";
import Reports from "./Reports";
import JobForm from "./JobForm";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  Settings as SettingsIcon,
  HelpCircle,
  LogOut,
  ChevronRight,
  ChevronDown,
  Plus,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import DashboardTopbar from "@/components/DashboardTopbar";
import Settings from "./Settings";
import Help from "./Help";
import Profile from "./Profile";
import { Card } from "@/components/ui/card";
import { Link } from "react-router-dom";

const Dashboard = () => {
  const navigate = useNavigate();
  // States
  const [stats, setStats] = useState<any[]>([]);
  const [activeJobs, setActiveJobs] = useState<any[]>([]);
  const [expandedJob, setExpandedJob] = useState<number | null>(null);
  const [showJobs, setShowJobs] = useState<boolean>(true);
  const [activeSection, setActiveSection] = useState<string>("dashboard"); // 👈 controls which main section is visible
  const [selectedJob, setSelectedJob] = useState<any | null>(null);

  const jobOptions = [
    { title: "Resume Screening", key: "screening" },
    { title: "Assessments", key: "assessments" },
    { title: "AI Interviews", key: "interviews" },
    { title: "Reports", key: "reports" },
  ];

  const generalOptions = [
    { title: "Settings", icon: SettingsIcon, key: "settings" },
    { title: "Help", icon: HelpCircle, key: "help" },
    //{ title: "Logout", icon: LogOut, key: "logout" },
  ];
  
  //This is the fuction to delete the job

  const deleteJob = async (jobId, token) => {
  try {
      if (!token) return;

    const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/routes/delete-job/${jobId}`, { 
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
  },
    });

    if (!response.ok) {
      throw new Error("Failed to delete job");
    }

    const data = await response.json();
    console.log(data.message);

  } catch (error) {
    console.error("Error deleting job:", error);
  }
  };

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;

        const response = await fetch(
          `${import.meta.env.VITE_BACKEND_URL}/routes/dashboard_essentials/dashboard-info`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );

        const text = await response.text();
        const data = JSON.parse(text);

        setStats([
          {
            title: "Total Jobs Posted",
            value: data.total_job_postings || 0,
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
            value:
              data.jobs?.filter((job: any) => job.status === "open").length || 0,
            icon: LayoutDashboard,
            gradient: "from-pink-600 to-pink-400",
          },
        ]);

        setActiveJobs(data.jobs || []);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      }
    };

    fetchDashboard();
  }, []);

  // 👇 Helper function for rendering the main section
  const handleGenerateApplyLink = (job: any) => {
    if (!job) return;
    try {
      const token = job.apply_token || job.id;
      const link = `${window.location.origin}/apply?token=${encodeURIComponent(token)}`;
      if (navigator && (navigator as any).clipboard && (navigator as any).clipboard.writeText) {
        (navigator as any).clipboard.writeText(link);
        alert("Apply link copied to clipboard:\n" + link);
      } else {
        // fallback
        window.prompt("Copy this link:", link);
      }
    } catch (err) {
      console.error(err);
      alert("Could not generate link");
    }
  };
  const renderMainContent = () => {
    switch (activeSection) {
      case "dashboard":
        return (
          <div className="rounded-2xl bg-card p-6 shadow-sm mt-3">
            {/* Header with Add Job button */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold mb-2">Welcome back, HR Manager</h1>
                <p className="text-muted-foreground">
                  Here's what's happening with your recruitment pipeline.
                </p>
              </div>

              {/* Add Job Button */}
              <Button
                onClick={() => setActiveSection("uploadJob")}
                className="bg-purple-600/50 text-white hover:bg-purple-500/70 flex items-center gap-2 rounded-md hover:shadow-none"
              >
                <Plus className="h-4 w-4" />
                Add Job
              </Button>

              
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {stats.map((stat) => (
                <div
                  key={stat.title}
                  className="relative overflow-hidden rounded-xl bg-muted/30 p-4"
                >
                  <div
                    className={`absolute inset-0 opacity-10 bg-gradient-to-br ${stat.gradient}`}
                  />
                  <div className="relative flex flex-row items-center justify-between pb-2">
                    <span className="text-sm font-medium">{stat.title}</span>
                    <stat.icon
                      className={`h-5 w-5 bg-gradient-to-br ${stat.gradient} bg-clip-text text-transparent`}
                    />
                  </div>
                  <div className="relative text-3xl font-bold">
                    {stat.value}
                  </div>
                </div>
              ))}
            </div>

            {/* Recent Activity */}
            <div className="relative overflow-hidden rounded-xl bg-muted/30 p-5">
              <div className="absolute inset-0 opacity-5 bg-gradient-to-br from-purple-600 to-blue-600" />
              <div className="relative">
                <h2 className="text-xl font-semibold mb-4">
                  Recent Activity
                </h2>
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div className="h-2 w-2 rounded-full bg-green-500" />
                    <p className="text-sm">
                      <span className="font-medium">
                        Senior Frontend Developer
                      </span>
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
              </div>
            </div>
          </div>
        );
      case "uploadJob":
        return <JobForm token={localStorage.getItem("token") || ""} />;

      case "screening":
        return <ResumeScreening jobId={selectedJob?.id} job={selectedJob} />;

      case "assessments":
        return <Assessments jobId={selectedJob?.id} job={selectedJob} />;

      case "interviews":
        return <AIInterviews jobId={selectedJob?.id} job={selectedJob} />;

      case "reports":
        return <Reports jobId={selectedJob?.id} job={selectedJob} />;

      case "settings":
        return <Settings />;

      case "help":
        return <Help />;

      case "profile":
        return <Profile />;

        case "jobDetails":
          if (!selectedJob) return null;
          return (
            <Card className="p-6 mt-4 border-none">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-semibold mb-1">{selectedJob.job_title}</h2>
                  <p className="text-blue-400">Status: {selectedJob.status || "Unknown"}</p>
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleGenerateApplyLink(selectedJob)}
                    className="rounded-md bg-indigo-600/60 text-white hover:bg-indigo-600/80"
                  >
                    Generate Apply Link
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={() => console.log("Edit", selectedJob.id)}
                    className="rounded-md bg-green-600/60 text-white hover:bg-green-600/80"
                  >
                    Edit
                  </Button>

                  {/* Zoha please redo this, this looks ugly */}
                  <Button
                    variant="destructive"
                    onClick={() => {
                      const confirmed = window.confirm(
                        "Are you sure you want to delete this job?"
                      );

                    if (confirmed) {
                      deleteJob(selectedJob.id, localStorage.getItem("token"));
                    }
                    }}
                    className="rounded-md bg-red-600/60 text-white hover:bg-red-600/80"
                    >
                    Delete
                  </Button>
                </div>
              </div>

              <Separator className="my-4" />

              <div className="space-y-3">
                <p>
                  <span className="font-semibold">Description:</span>{" "}
                  {selectedJob.description || "No description available."}
                </p>
                <p>
                  <span className="font-semibold">Location:</span>{" "}
                  {selectedJob.location || "Not specified"}
                </p>
                <p>
                  <span className="font-semibold">Posted On:</span>{" "}
                  {selectedJob.posted_on ? new Date(selectedJob.posted_on).toLocaleDateString() : "N/A"}
                </p>
              </div>
            </Card>
          );

      default:
        return null;
    }
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className="w-80 p-4">
        <div className="h-full rounded-3xl bg-card p-4 shadow-sm">
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

          <ScrollArea className="h-[85vh] pr-2">
            {/* MENU */}
            <h3 className="text-xs font-semibold text-gray-500 mb-2">MENU</h3>

            {/* Dashboard */}
            <Button
              variant="ghost"
              className={`w-full justify-start text-left mb-1 px-3 py-2 ${
                activeSection === "dashboard"
                  ? "bg-secondary/60 text-white font-medium"
                  : "hover:bg-secondary/60"
              }`}
              onClick={() => setActiveSection("dashboard")}
            >
              <LayoutDashboard className="mr-2 h-4 w-4" />
              Dashboard
            </Button>

            {/* Active Jobs */}
            <div className="mb-2">
              <Button
                variant="ghost"
                onClick={() => setShowJobs(!showJobs)}
                className="w-full justify-between text-left px-3 py-2 hover:bg-secondary/60 transition-colors duration-300"
              >
                <div className="flex items-center">
                  <Briefcase className="mr-2 h-4 w-4" />
                  Active Jobs
                </div>
                <ChevronDown
                  className={`h-4 w-4 opacity-60 transition-transform duration-300 ${
                    showJobs ? "rotate-180" : "rotate-0"
                  }`}
                />
              </Button>

              {/* Smooth accordion for jobs */}
              <div
                className={`overflow-hidden transition-[max-height,opacity,margin] duration-300 ease-in-out
                  ${showJobs ? "max-h-[1000px] opacity-100 mt-2" : "max-h-0 opacity-0 mt-0"}
                `}
              >
                {activeJobs.map((job) => (
                  <div key={job.id} className="mb-1">
                    <Button
                      variant="ghost"
                      onClick={() => {
                        setSelectedJob(job);
                        setExpandedJob(expandedJob === job.id ? null : job.id);
                        setActiveSection("jobDetails");
                      }}
                      className={`w-[94%] justify-between text-left px-3 py-2 rounded-full transition-colors duration-300
                        ${expandedJob === job.id ? "bg-secondary/60" : "hover:bg-secondary/70"}
                      `}
                    >
                      <span className="truncate">{job.job_title}</span>
                      {expandedJob === job.id ? (
                        <ChevronDown className="h-4 w-4 opacity-60 transition-transform duration-300 rotate-180" />
                      ) : (
                        <ChevronRight className="h-4 w-4 opacity-60 transition-transform duration-300" />
                      )}
                    </Button>

                    {/* Smooth dropdown for job sub-options */}
                    <div
                      className={`pl-4 overflow-hidden transition-[max-height,opacity,margin] duration-300 ease-in-out
                        ${expandedJob === job.id ? "max-h-60 opacity-100 mt-1" : "max-h-0 opacity-0 mt-0"}
                      `}
                    >
                      {jobOptions.map((option) => (
                        <Button
                          key={option.key}
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            // ensure selected job is set, then switch section
                            setSelectedJob(job);
                            setActiveSection(option.key);
                          }}
                          className={`w-[90%] justify-start text-sm transition-colors duration-200
                            ${
                              activeSection === option.key
                                ? "text-primary font-medium bg-secondary/40"
                                : "text-muted-foreground hover:text-primary hover:bg-secondary/60"
                            }
                          `}
                        >
                          {option.title}
                        </Button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          
            <Separator className="my-4" />

            {/* GENERAL */}
            <h3 className="text-xs font-semibold text-gray-500 mb-2">GENERAL</h3>
            {generalOptions.map((option) => (
              <Button
                key={option.key}
                variant="ghost"
                className={`w-full justify-start mb-1 px-3 py-2 ${
                  activeSection === option.key
                    ? "bg-secondary/60 text-primary font-medium"
                    : "hover:bg-secondary/60"
                }`}
                onClick={() => setActiveSection(option.key)}
              >
                <option.icon className="mr-2 h-4 w-4" />
                {option.title}
              </Button>
            ))}
          </ScrollArea>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 p-4 overflow-y-auto">
        <DashboardTopbar
          jobs={activeJobs}
          hideSearch={activeSection === "settings" || activeSection === "help"}
          onJobSelect={(job) => {
            setSelectedJob(job);
            setActiveSection("jobDetails");
          }}
          onMenuSelect={(key) => {
            if (key === 'profile') setActiveSection('profile');
            if (key === 'logout') {
              (async () => {
                try {
                  const { supabase } = await import("@/supabaseClient");
                  await supabase.auth.signOut();
                } catch (err) {
                  console.error("Logout error:", err);
                }
                localStorage.removeItem("token");
                navigate("/hr-login");
              })();
            }
          }}
        />
        {renderMainContent()}
      </div>
    </div>
  );
};

export default Dashboard;