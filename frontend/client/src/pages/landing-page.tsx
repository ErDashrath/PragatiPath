import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { 
  BookOpen, 
  Users, 
  Trophy, 
  Clock,
  ArrowRight,
  Play,
  CheckCircle,
  Star,
  Target,
  Brain,
  TrendingUp,
  Award,
  Sparkles
} from "lucide-react";

export default function LandingPage() {
  const [, navigate] = useLocation();

  const handleGetStarted = () => {
    navigate("/auth");
  };

  const handleStartLearning = () => {
    navigate("/auth");
  };

  const stats = [
    { icon: BookOpen, value: "1000+", label: "Lessons" },
    { icon: Users, value: "50k+", label: "Students" },
    { icon: Trophy, value: "95%", label: "Success Rate" },
    { icon: Clock, value: "24/7", label: "Support" }
  ];

  const features = [
    {
      title: "AI-Powered Learning",
      description: "Adaptive algorithms that personalize your learning experience",
      icon: Brain
    },
    {
      title: "Progress Analytics",
      description: "Comprehensive tracking of your academic growth and achievements",
      icon: TrendingUp
    },
    {
      title: "Achievement System",
      description: "Gamified learning with badges and certificates to motivate progress",
      icon: Award
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-emerald-500/10 rounded-full blur-2xl animate-bounce"></div>
      </div>

      {/* Glass Morphism Header */}
      <motion.header 
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="backdrop-blur-xl bg-black/10 border-b border-white/10 sticky top-0 z-50"
      >
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <motion.div 
              className="flex items-center space-x-3"
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 400, damping: 10 }}
            >
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center overflow-hidden shadow-lg shadow-purple-500/25">
                <img 
                  src="/logo.png" 
                  alt="PragatiPath Logo" 
                  className="w-full h-full object-cover rounded-2xl"
                />
              </div>
              <span className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-purple-200">
                PragatiPath
              </span>
            </motion.div>
            
            <nav className="hidden lg:flex items-center space-x-8">
              {["Features", "About", "Contact"].map((item, index) => (
                <motion.a
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="text-white/70 hover:text-white font-medium transition-all duration-300 relative group"
                  whileHover={{ y: -2 }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 + 0.5 }}
                >
                  {item}
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-purple-400 to-pink-400 group-hover:w-full transition-all duration-300"></span>
                </motion.a>
              ))}
            </nav>

            <div className="flex items-center space-x-4">
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button 
                  variant="ghost" 
                  onClick={() => navigate("/auth")}
                  className="text-white/70 hover:text-white font-medium backdrop-blur-sm hover:bg-white/10 border border-white/10 rounded-xl px-6 py-3 transition-all duration-300"
                >
                  Sign In
                </Button>
              </motion.div>
              <motion.div
                whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(168, 85, 247, 0.4)" }}
                whileTap={{ scale: 0.95 }}
              >
                <Button 
                  onClick={handleGetStarted} 
                  className="text-white font-semibold px-8 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 shadow-lg shadow-purple-500/25 transition-all duration-300 border-0"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  Get Started
                </Button>
              </motion.div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Hero Section - Split Layout */}
      <section className="min-h-screen flex items-center relative z-10">
        <div className="container mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left Side - Content */}
            <motion.div 
              className="space-y-8"
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 1, ease: "easeOut" }}
            >
              <div className="space-y-6">
                <motion.div 
                  className="inline-flex items-center px-6 py-3 backdrop-blur-xl bg-white/10 border border-white/20 rounded-full"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <Sparkles className="w-4 h-4 mr-2 text-purple-300" />
                  <span className="text-white/90 font-medium text-sm">Your AI-powered adaptive learning companion</span>
                </motion.div>
                
                <motion.h1 
                  className="text-6xl lg:text-8xl font-black text-white leading-tight"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5, duration: 0.8 }}
                >
                  Welcome to{" "}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-purple-600 animate-pulse">
                    PragatiPath
                  </span>
                </motion.h1>
                
                <motion.p 
                  className="text-xl text-white/70 leading-relaxed max-w-lg font-light"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 }}
                >
                  Experience personalized learning that adapts to your pace. Master concepts, track progress, and achieve excellence in your educational journey.
                </motion.p>
              </div>

              <motion.div 
                className="flex flex-col sm:flex-row gap-4"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 }}
              >
                <motion.div
                  whileHover={{ scale: 1.05, boxShadow: "0 0 40px rgba(168, 85, 247, 0.6)" }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button 
                    size="lg" 
                    onClick={handleStartLearning}
                    className="px-10 py-4 text-lg font-bold text-white rounded-2xl bg-gradient-to-r from-purple-500 via-pink-500 to-purple-600 hover:from-purple-600 hover:via-pink-600 hover:to-purple-700 shadow-2xl shadow-purple-500/25 border-0 transition-all duration-300"
                  >
                    Start Learning Now
                    <ArrowRight className="ml-3 w-6 h-6" />
                  </Button>
                </motion.div>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button 
                    size="lg" 
                    variant="outline"
                    onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
                    className="px-10 py-4 text-lg font-semibold border-2 border-white/20 rounded-2xl hover:bg-white/10 backdrop-blur-sm text-white transition-all duration-300"
                  >
                    <Play className="mr-3 w-6 h-6" />
                    Watch Demo
                  </Button>
                </motion.div>
              </motion.div>

              {/* Quick Stats */}
              <motion.div 
                className="grid grid-cols-3 gap-6 pt-8"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.1 }}
              >
                {stats.slice(0, 3).map((stat, index) => (
                  <motion.div 
                    key={index} 
                    className="text-center backdrop-blur-sm bg-white/5 p-4 rounded-2xl border border-white/10"
                    whileHover={{ scale: 1.05, backgroundColor: "rgba(255, 255, 255, 0.1)" }}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.2 + index * 0.1 }}
                  >
                    <div className="text-3xl font-black text-white mb-2">{stat.value}</div>
                    <div className="text-sm text-white/70 font-medium">{stat.label}</div>
                  </motion.div>
                ))}
              </motion.div>
            </motion.div>

            {/* Right Side - Visual */}
            <motion.div 
              className="relative"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
            >
              <div className="relative backdrop-blur-xl bg-white/10 border border-white/20 rounded-3xl p-8 shadow-2xl">
                <motion.div 
                  className="aspect-square relative overflow-hidden rounded-3xl"
                  whileHover={{ scale: 1.02 }}
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                >
                  <img 
                    src="/landing-hero.jpg" 
                    alt="PragatiPath Learning Platform"
                    className="w-full h-full object-cover"
                  />
                  
                  {/* Floating Cards */}
                  <motion.div 
                    className="absolute -top-6 -right-6 backdrop-blur-xl bg-white/20 border border-white/30 p-4 rounded-2xl shadow-2xl"
                    initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
                    animate={{ opacity: 1, scale: 1, rotate: 0 }}
                    transition={{ delay: 1.5, type: "spring", stiffness: 300 }}
                    whileHover={{ scale: 1.1, rotate: 5 }}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 rounded-full flex items-center justify-center bg-gradient-to-r from-yellow-400 to-orange-500 shadow-lg">
                        <Trophy className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <div className="font-bold text-white">Achievement</div>
                        <div className="text-sm text-white/70">Level Completed</div>
                      </div>
                    </div>
                  </motion.div>
                  
                  <motion.div 
                    className="absolute -bottom-6 -left-6 backdrop-blur-xl bg-white/20 border border-white/30 p-4 rounded-2xl shadow-2xl"
                    initial={{ opacity: 0, scale: 0.8, rotate: 10 }}
                    animate={{ opacity: 1, scale: 1, rotate: 0 }}
                    transition={{ delay: 1.7, type: "spring", stiffness: 300 }}
                    whileHover={{ scale: 1.1, rotate: -5 }}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 rounded-full flex items-center justify-center bg-gradient-to-r from-emerald-400 to-blue-500 shadow-lg">
                        <TrendingUp className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <div className="font-bold text-white">Progress</div>
                        <div className="text-sm text-white/70">85% Complete</div>
                      </div>
                    </div>
                  </motion.div>
                </motion.div>
                
                {/* Decorative Elements */}
                <div className="absolute -top-4 -left-4 w-24 h-24 bg-gradient-to-r from-purple-500/30 to-pink-500/30 rounded-full blur-xl animate-pulse"></div>
                <div className="absolute -bottom-4 -right-4 w-20 h-20 bg-gradient-to-r from-blue-500/30 to-emerald-500/30 rounded-full blur-xl animate-pulse delay-1000"></div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-32 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-900/50 to-purple-900/50"></div>
        <div className="container mx-auto px-6 relative z-10">
          <motion.div 
            className="text-center mb-20"
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <motion.div 
              className="inline-flex items-center px-6 py-3 backdrop-blur-xl bg-white/10 border border-white/20 rounded-full mb-8"
              whileHover={{ scale: 1.05 }}
            >
              <Star className="w-5 h-5 mr-2 text-purple-300" />
              <span className="text-white/90 font-medium">Features</span>
            </motion.div>
            <motion.h2 
              className="text-5xl lg:text-7xl font-black text-white mb-8"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.8 }}
              viewport={{ once: true }}
            >
              Why Choose{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                PragatiPath?
              </span>
            </motion.h2>
            <motion.p 
              className="text-xl text-white/70 max-w-3xl mx-auto font-light"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.8 }}
              viewport={{ once: true }}
            >
              Experience the future of learning with our advanced AI-powered platform designed to help you succeed
            </motion.p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 mt-16">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.2, duration: 0.8 }}
                viewport={{ once: true }}
                whileHover={{ 
                  scale: 1.05, 
                  rotateY: 5,
                  boxShadow: "0 25px 50px -12px rgba(168, 85, 247, 0.25)"
                }}
                className="perspective-1000"
              >
                <Card className="border-0 backdrop-blur-xl bg-white/10 border border-white/20 rounded-3xl overflow-hidden shadow-2xl hover:shadow-purple-500/25 transition-all duration-500">
                  <CardContent className="p-10 text-center">
                    <motion.div 
                      className="w-20 h-20 mx-auto rounded-3xl mb-8 flex items-center justify-center bg-gradient-to-br from-purple-500 via-pink-500 to-purple-600 shadow-2xl shadow-purple-500/25"
                      whileHover={{ 
                        rotate: 360, 
                        scale: 1.1,
                        boxShadow: "0 0 40px rgba(168, 85, 247, 0.6)"
                      }}
                      transition={{ duration: 0.6 }}
                    >
                      <feature.icon className="w-10 h-10 text-white" />
                    </motion.div>
                    <h3 className="text-2xl font-bold text-white mb-6">{feature.title}</h3>
                    <p className="text-white/70 leading-relaxed text-lg font-light">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600 via-pink-600 to-purple-800"></div>
        <div className="absolute inset-0 opacity-20">
          <div className="w-full h-full" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}></div>
        </div>
        
        <div className="container mx-auto px-6 text-center relative z-10">
          <motion.h2 
            className="text-5xl lg:text-7xl font-black text-white mb-8"
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            Ready to Transform Your{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-orange-300">
              Learning?
            </span>
          </motion.h2>
          <motion.p 
            className="text-2xl text-white/80 mb-12 max-w-3xl mx-auto font-light"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            viewport={{ once: true }}
          >
            Join thousands of students who are already achieving their academic goals with our AI-powered platform
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            viewport={{ once: true }}
            whileHover={{ 
              scale: 1.05, 
              boxShadow: "0 0 60px rgba(255, 255, 255, 0.3)" 
            }}
            whileTap={{ scale: 0.95 }}
          >
            <Button 
              size="lg" 
              onClick={handleGetStarted}
              className="px-12 py-6 text-xl font-bold bg-white text-purple-600 rounded-2xl hover:bg-gray-100 shadow-2xl transition-all duration-300 border-0"
            >
              <Sparkles className="mr-4 w-6 h-6" />
              Start Your Journey Today
              <ArrowRight className="ml-4 w-6 h-6" />
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black/50 backdrop-blur-xl border-t border-white/10 py-20">
        <div className="container mx-auto px-6">
          <motion.div 
            className="text-center"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <div className="flex items-center justify-center space-x-4 mb-8">
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center bg-gradient-to-r from-purple-500 to-pink-500 shadow-lg shadow-purple-500/25">
                <BookOpen className="w-8 h-8 text-white" />
              </div>
              <span className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-purple-200">
                PragatiPath
              </span>
            </div>
            <p className="text-white/60 mb-12 max-w-md mx-auto text-lg font-light">
              Your AI-powered adaptive learning companion for academic excellence
            </p>
            <div className="border-t border-white/10 pt-12">
              <p className="text-white/40 font-light">
                © 2025 PragatiPath. All rights reserved.
              </p>
            </div>
          </motion.div>
        </div>
      </footer>
    </div>
  );
}