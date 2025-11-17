import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Card, CardContent } from "@/components/ui/card";
import { Target, Shield, TrendingUp, Users } from "lucide-react";
import { motion } from "framer-motion";


const About = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="pt-24 pb-20">
        <div className="container mx-auto px-6">
          {/* Header */}
          <div className="max-w-4xl mx-auto text-center mb-16 animate-fade-in">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Our <span className="bg-gradient-primary bg-clip-text text-transparent">Mission</span>
            </h1>
            <p className="text-xl text-muted-foreground">
              Transforming recruitment through intelligent automation and ethical AI
            </p>
          </div>

          {/* Mission Section */}
          <section className="max-w-4xl mx-auto mb-20">
            <Card className="border-border bg-card/50 animate-scale-in">
              <CardContent className="p-8 md:p-12">
                <p className="text-lg text-muted-foreground leading-relaxed mb-6">
                  Traditional hiring processes are plagued by inefficiencies: manual resume screening is time-consuming, 
                  subjective evaluations introduce bias, and inconsistent interview standards lead to poor candidate experiences. 
                </p>
                <p className="text-lg text-muted-foreground leading-relaxed">
                  Our AI-Powered Hiring Automation System addresses these challenges head-on by leveraging Natural Language Processing, 
                  deep learning, and multimodal emotional analysis to create a fair, efficient, and accurate recruitment pipeline.
                </p>
              </CardContent>
            </Card>
          </section>

          {/* Why AI Section */}
          <section className="mb-20">
            <h2 className="text-3xl md:text-5xl font-bold mb-12 text-center">
              Why AI in Hiring?
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
  
              {/* Traditional Hiring Card */}
              <motion.div
                initial={{ opacity: 0, y: 60 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                viewport={{ once: true, amount: 0.2 }}
              >
                <Card className="border-border bg-card hover:shadow-elegant transition-all duration-300">
                  <CardContent className="p-8">
                    <h3 className="text-xl font-semibold mb-4 text-destructive">Traditional Hiring</h3>
                    <ul className="space-y-3 text-muted-foreground">
                      <li className="flex items-start gap-2"><span className="text-destructive mt-1">•</span><span>Weeks of manual resume screening</span></li>
                      <li className="flex items-start gap-2"><span className="text-destructive mt-1">•</span><span>Unconscious bias in evaluations</span></li>
                      <li className="flex items-start gap-2"><span className="text-destructive mt-1">•</span><span>Inconsistent interview standards</span></li>
                      <li className="flex items-start gap-2"><span className="text-destructive mt-1">•</span><span>Limited candidate insights</span></li>
                      <li className="flex items-start gap-2"><span className="text-destructive mt-1">•</span><span>High cost per hire</span></li>
                    </ul>
                  </CardContent>
                </Card>
              </motion.div>

              {/* AI-Driven Hiring Card */}
              <motion.div
                initial={{ opacity: 0, y: 60 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                viewport={{ once: true, amount: 0.2 }}
              >
                <Card className="border-primary/50 bg-gradient-hero hover:shadow-glow transition-all duration-300">
                  <CardContent className="p-8">
                    <h3 className="text-xl font-semibold mb-4 text-primary">AI-Driven Hiring</h3>
                    <ul className="space-y-3 text-foreground">
                      <li className="flex items-start gap-2"><span className="text-primary mt-1">✓</span><span>Instant automated screening</span></li>
                      <li className="flex items-start gap-2"><span className="text-primary mt-1">✓</span><span>Objective, unbiased evaluations</span></li>
                      <li className="flex items-start gap-2"><span className="text-primary mt-1">✓</span><span>Standardized AI interviews</span></li>
                      <li className="flex items-start gap-2"><span className="text-primary mt-1">✓</span><span>Deep behavioral & emotional analysis</span></li>
                      <li className="flex items-start gap-2"><span className="text-primary mt-1">✓</span><span>Reduced time & cost to hire</span></li>
                    </ul>
                  </CardContent>
                </Card>
              </motion.div>

            </div>
          </section>

          {/* Trust & Transparency */}
          <section className="mb-20">
            <h2 className="text-3xl md:text-5xl font-bold mb-12 text-center">
              Trust & Transparency
            </h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                {
                  icon: Shield,
                  title: "Ethical AI",
                  description: "Built with fairness and transparency at the core"
                },
                {
                  icon: Target,
                  title: "Unbiased Evaluation",
                  description: "Objective assessment free from human prejudice"
                },
                {
                  icon: TrendingUp,
                  title: "Data-Driven",
                  description: "Decisions backed by comprehensive analytics"
                },
                {
                  icon: Users,
                  title: "Fair Process",
                  description: "Equal opportunity for every candidate"
                }
              ].map((item, index) => (
                <Card 
                  key={index}
                  className="border-border bg-card hover:shadow-elegant transition-all duration-300 group animate-scale-in"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <CardContent className="p-6 text-center">
                    <div className="bg-gradient-primary p-3 rounded-lg w-fit mx-auto mb-4 group-hover:shadow-glow transition-all duration-300">
                      <item.icon className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="font-semibold mb-2">{item.title}</h3>
                    <p className="text-sm text-muted-foreground">{item.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          {/* Project Info */}
          {/* <section className="max-w-4xl mx-auto">
            <Card className="border-border bg-card/50">
              <CardContent className="p-8 md:p-12 text-center">
                <h3 className="text-2xl font-bold mb-4">Final Year Industrial Project</h3>
                <p className="text-muted-foreground mb-2">
                  Department of Computer Science
                </p>
                <p className="text-muted-foreground font-medium">
                  FAST National University of Computer and Emerging Sciences (NUCES)
                </p>
                <p className="text-muted-foreground">
                  Karachi Campus
                </p>
              </CardContent>
            </Card>
          </section> */}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default About;