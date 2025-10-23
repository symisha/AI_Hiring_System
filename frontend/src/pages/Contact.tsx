import { useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Mail, MapPin, Send } from "lucide-react";

const Contact = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: ""
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast({
      title: "Message Sent!",
      description: "We'll get back to you as soon as possible.",
    });
    setFormData({ name: "", email: "", message: "" });
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="pt-24 pb-20">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="text-center mb-16 animate-fade-in">
              <h1 className="text-4xl md:text-6xl font-bold mb-6">
                Get in <span className="bg-gradient-primary bg-clip-text text-transparent">Touch</span>
              </h1>
              <p className="text-xl text-muted-foreground">
                Have questions about our AI hiring system? We'd love to hear from you.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {/* Contact Form */}
              <Card className="border-border bg-card animate-scale-in">
                <CardContent className="p-8">
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium mb-2">
                        Name
                      </label>
                      <Input
                        id="name"
                        type="text"
                        placeholder="Your name"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        required
                        className="bg-secondary border-border"
                      />
                    </div>

                    <div>
                      <label htmlFor="email" className="block text-sm font-medium mb-2">
                        Email
                      </label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="your.email@example.com"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        required
                        className="bg-secondary border-border"
                      />
                    </div>

                    <div>
                      <label htmlFor="message" className="block text-sm font-medium mb-2">
                        Message
                      </label>
                      <Textarea
                        id="message"
                        placeholder="Tell us about your inquiry..."
                        value={formData.message}
                        onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                        required
                        rows={6}
                        className="bg-secondary border-border resize-none"
                      />
                    </div>

                    <Button type="submit" variant="hero" size="lg" className="w-full">
                      Send Message
                      <Send className="ml-2 h-4 w-4" />
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Contact Info */}
              <div className="space-y-6 animate-fade-in-up">
                <Card className="border-border bg-card hover:shadow-elegant transition-all duration-300">
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="bg-gradient-primary p-3 rounded-lg">
                        <MapPin className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg mb-2">Location</h3>
                        <p className="text-muted-foreground">
                          FAST National University of Computer and Emerging Sciences (NUCES)
                          <br />
                          Karachi Campus
                          <br />
                          Department of Computer Science
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-border bg-card hover:shadow-elegant transition-all duration-300">
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="bg-gradient-primary p-3 rounded-lg">
                        <Mail className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg mb-2">Email</h3>
                        <a 
                          href="mailto:contact@aihiring.edu" 
                          className="text-muted-foreground hover:text-primary transition-colors"
                        >
                          contact@aihiring.edu
                        </a>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-primary/50 bg-gradient-hero">
                  <CardContent className="p-6">
                    <h3 className="font-semibold text-lg mb-2">Office Hours</h3>
                    <p className="text-muted-foreground mb-2">
                      Monday - Friday: 9:00 AM - 5:00 PM
                    </p>
                    <p className="text-sm text-muted-foreground">
                      For urgent inquiries, please contact us via email and we'll respond within 24 hours.
                    </p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Contact;