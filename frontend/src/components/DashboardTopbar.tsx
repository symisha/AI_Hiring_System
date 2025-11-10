import React from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Bell, Search, ChevronDown } from "lucide-react";

const DashboardTopbar: React.FC = () => {
  const [search, setSearch] = React.useState("");
  const [notifications] = React.useState(3); // placeholder count

  return (
    <div className="mb-3">
        <div className="rounded-2xl bg-card p-3 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          {/* Left: Search */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <span className="absolute inset-y-0 left-3 flex items-center text-muted-foreground">
                <Search className="w-4 h-4" />
              </span>
                <Input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search candidates, jobs..."
                  className="pl-10 h-12 rounded-full border-0 focus-visible:ring-0"
                />
            </div>
          </div>

          {/* Right: notifications + profile */}
          <div className="flex items-center gap-3">
            <Button variant="ghost" className="relative p-2 rounded-full">
              <Bell className="w-5 h-5" />
              {notifications > 0 && (
                <span className="absolute -top-1 -right-1 inline-flex items-center justify-center rounded-full bg-red-500 text-white text-[10px] h-4 w-4">
                  {notifications}
                </span>
              )}
            </Button>

            <Button variant="ghost" className="flex items-center gap-2 rounded-full px-2 py-1">
              <Avatar className="h-12 w-12">
                <AvatarImage src="/src/assets/avatar-placeholder.png" alt="Profile" />
                <AvatarFallback>MI</AvatarFallback>
              </Avatar>
              <div className="hidden md:flex flex-col items-start leading-tight">
                <span className="text-sm font-medium">HR Manager</span>
                <span className="text-xs text-muted-foreground">Admin</span>
              </div>
              <ChevronDown className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardTopbar;
