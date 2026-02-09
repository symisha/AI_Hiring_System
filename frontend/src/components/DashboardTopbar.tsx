import React, { useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Bell, Search, ChevronDown } from "lucide-react";

type DashboardTopbarProps = {
  onMenuSelect?: (key: string) => void;
  hideSearch?: boolean;
  jobs?: any[];
  onJobSelect?: (job: any) => void;
};

const DashboardTopbar: React.FC<DashboardTopbarProps> = ({ onMenuSelect, hideSearch = false, jobs = [], onJobSelect }) => {
  const [search, setSearch] = React.useState("");
  const [showSuggestions, setShowSuggestions] = React.useState(false);
  const [notifications] = React.useState(3);
  const [openProfileMenu, setOpenProfileMenu] = React.useState(false);

  // Ref to detect clicks outside
  const profileRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setOpenProfileMenu(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className="mb-3 relative">
      <div className="rounded-2xl bg-card p-3 shadow-sm">
        <div className="flex items-center justify-between gap-3">

          {/* Search (hidden on some pages) */}
          {!hideSearch ? (
            <div className="flex-1 max-w-md">
              <div className="relative">
                <span className="absolute inset-y-0 left-3 flex items-center text-muted-foreground">
                  <Search className="w-4 h-4" />
                </span>
                <Input
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    setShowSuggestions(Boolean(e.target.value));
                  }}
                  onFocus={() => setShowSuggestions(Boolean(search))}
                  onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
                  placeholder="Search candidates, jobs..."
                  className="pl-10 h-12 rounded-full border-0 focus-visible:ring-0"
                />

                {/* Suggestions dropdown */}
                {showSuggestions && search.trim().length > 0 && (
                  <div className="absolute left-0 right-0 mt-2 bg-card border rounded-lg shadow-lg z-50 max-h-60 overflow-auto">
                    {jobs && jobs.length > 0 ? (
                      jobs
                        .filter((j: any) =>
                          (j.title || "").toLowerCase().includes(search.toLowerCase())
                        )
                        .slice(0, 8)
                        .map((job: any) => (
                          <button
                            key={job.id || job.title}
                            onMouseDown={(e) => e.preventDefault()}
                            onClick={() => {
                              setSearch("");
                              setShowSuggestions(false);
                              onJobSelect && onJobSelect(job);
                            }}
                            className="w-full text-left px-4 py-2 hover:bg-secondary/40"
                          >
                            <div className="font-medium">{job.title}</div>
                            <div className="text-xs text-muted-foreground">{job.location || ""}</div>
                          </button>
                        ))
                    ) : (
                      <div className="px-4 py-2 text-sm text-muted-foreground">No jobs available</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex-1" />
          )}

          {/* Right section */}
          <div className="flex items-center gap-3">

            {/* Notification Icon */}
            <Button variant="ghost" className="relative p-2 rounded-full">
              <Bell className="w-5 h-5" />
              {notifications > 0 && (
                <span className="absolute -top-1 -right-1 inline-flex items-center justify-center rounded-full bg-red-500 text-white text-[10px] h-4 w-4">
                  {notifications}
                </span>
              )}
            </Button>

            {/* Profile Button */}
            <div className="relative" ref={profileRef}>
              <Button
                variant="ghost"
                className="flex items-center gap-2 rounded-full px-2 py-1 hover:bg-transparent"
                onClick={() => setOpenProfileMenu(!openProfileMenu)}
              >
                <Avatar className="h-12 w-12">
                  <AvatarImage src="/src/assets/avatar-placeholder.png" alt="Profile" />
                  <AvatarFallback>MI</AvatarFallback>
                </Avatar>

                <div className="hidden md:flex flex-col items-start leading-tight">
                  <span className="text-sm font-medium">HR Manager</span>
                  <span className="text-xs text-muted-foreground">Admin</span>
                </div>

                <ChevronDown
                  className={`w-4 h-4 ml-1 transition-transform ${
                    openProfileMenu ? "rotate-180" : ""
                  }`}
                />
              </Button>

              {/* Dropdown Menu */}
              <div
                className={`absolute right-0 mt-2 w-48 bg-card border rounded-xl shadow-lg p-2 z-50
                  transform origin-top-right transition-all duration-200 ease-out
                  ${openProfileMenu ? "opacity-100 scale-y-100" : "opacity-0 scale-y-0 pointer-events-none"}
                `}
              >
                <button
                  className="w-full text-left px-3 py-2 rounded-md hover:bg-secondary/50"
                  onClick={() => {
                    setOpenProfileMenu(false);
                    onMenuSelect && onMenuSelect("profile");
                  }}
                >
                  Profile
                </button>
                <button
                  className="w-full text-left px-3 py-2 rounded-md hover:bg-secondary/50 text-red-500"
                  onClick={() => {
                    setOpenProfileMenu(false);
                    onMenuSelect && onMenuSelect("logout");
                  }}
                >
                  Logout
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardTopbar;
