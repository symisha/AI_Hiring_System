import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { FileText, CheckCircle, MessageSquare, BarChart, ArrowRight } from "lucide-react";
import heroImage from "@/assets/hero.jpg";
import Reveal from "@/components/ui/reveal";

const Index = () => {
  const features = [
    {
      icon: FileText,
      title: "Resume Screening",
      description: "AI-powered analysis of resumes with intelligent ranking and skill matching."
    },
    {
      icon: CheckCircle,
      title: "AI Assessments",
      description: "Role-specific tests generated automatically to evaluate candidate competencies."
    },
    {
      icon: MessageSquare,
      title: "AI Interviews",
      description: "Conduct fair, unbiased interviews with emotional and behavioral analysis."
    },
    {
      icon: BarChart,
      title: "Comprehensive Reports",
      description: "Data-driven insights with top candidate recommendations and detailed analytics."
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center pt-24 pb-20 overflow-hidden" style={{ minHeight: '100vh' }}>
        <div className="absolute inset-0 bg-gradient-hero opacity-50" />
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `url(${heroImage})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            // filter: 'blur(8px)',
            // opacity: 0.1
          }}
        />
        
        <div className="container mx-auto px-6 relative z-10">
          <div className="max-w-4xl mx-auto text-center animate-fade-in">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              Revolutionize Hiring with{" "}
              <span className="bg-gradient-primary bg-clip-text text-transparent">
                AI-Powered Automation
              </span>
            </h1>
            <p className="text-xl text-white mb-10 max-w-2xl mx-auto">
              Streamline your recruitment process from resume screening to AI interviews. 
              Reduce hiring time, eliminate bias, and find the perfect candidates faster.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in-up">
              <Link to="/hr-login">
                <Button variant="hero" size="lg" className="w-full sm:w-auto">
                  Get Started Today
                  {/* <ArrowRight className="ml-2 h-5 w-5" /> */}
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-card/30">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-4">
              Intelligent Features for Modern Hiring
            </h2>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              Leverage cutting-edge AI technologies to transform your recruitment workflow
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 auto-rows-fr">
            {features.map((feature, index) => (
              <Reveal key={index} delay={index * 100}>
                <Card 
                  className="border-border bg-card transition-transform duration-300 hover:scale-[1.02] hover:shadow-elegant group h-full flex flex-col"
                >
                  <CardContent className="p-6 flex-1">
                    <div className="bg-gradient-primary p-3 rounded-lg w-fit mb-4 group-hover:shadow-glow transition-shadow duration-300">
                      <feature.icon className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground">{feature.description}</p>
                  </CardContent>
                </Card>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* AI Workflow Section */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl md:text-5xl font-bold mb-12 text-center">
              How It Works
            </h2>
            
            <div className="space-y-8">
              {[
                { step: "1", title: "Resume Screening", desc: "AI automatically fetches and analyzes resumes from your email, ranking candidates by relevance" },
                { step: "2", title: "Smart Assessments", desc: "Generate role-specific tests to evaluate technical skills and competencies" },
                { step: "3", title: "AI-Powered Interviews", desc: "Conduct fair, unbiased interviews with real-time emotional and behavioral analysis" },
                { step: "4", title: "Actionable Reports", desc: "Receive comprehensive reports with top 3 candidate recommendations and detailed insights" }
              ].map((item, index) => (
                <Reveal key={index} delay={index * 150}>
                  <div 
                    className="flex gap-6 items-start"
                  >
                    <div className="bg-gradient-primary text-white font-bold rounded-full w-12 h-12 flex items-center justify-center flex-shrink-0 shadow-glow">
                      {item.step}
                    </div>
                    <div>
                      <h3 className="font-semibold text-xl mb-2">{item.title}</h3>
                      <p className="text-muted-foreground">{item.desc}</p>
                    </div>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-hero border-y border-border">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-5xl font-bold mb-6">
            Ready to Transform Your Hiring Process?
          </h2>
          <p className="text-muted-foreground text-lg mb-8 max-w-2xl mx-auto">
            Join forward-thinking organizations leveraging AI for fair, efficient, and accurate recruitment
          </p>
          <Link to="/contact">
            <Button variant="hero" size="lg">
              Get Started Today
              {/* <ArrowRight className="ml-2 h-5 w-5" /> */}
            </Button>
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Index;