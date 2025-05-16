import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { LineChart, Brain, Target, Trophy, Code, Users } from 'lucide-react';

export const About = () => {
  return (
    <>
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32">
          <div className="container px-4 md:px-6">
            <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
              <div className="space-y-4">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl xl:text-6xl/none">
                  Revolutionizing Esports Betting with AI
                </h1>
                <p className="max-w-[600px] md:text-xl">
                  Q-BET is a team of data scientists, engineers, and CS2
                  enthusiasts using reinforcement learning to predict esports
                  outcomes with unprecedented accuracy.
                </p>
                <div className="flex flex-col gap-2 min-[400px]:flex-row">
                  <Button className="bg-green-500 hover:bg-green-600">
                    Our Technology
                  </Button>
                  <Button
                    variant="outline"
                    className="border-green-500 text-green-500 hover:bg-green-500/10"
                  >
                    View Results
                  </Button>
                </div>
              </div>
              <div className="relative h-[300px] lg:h-[400px] rounded-lg overflow-hidden">
                <img
                  src="/placeholder.svg?height=400&width=600"
                  alt="CS2 gameplay with data overlays"
                  className="object-cover"
                />
              </div>
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
                  Our Mission
                </h2>
                <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  We combine deep reinforcement learning with comprehensive CS2
                  game data to create predictive models that outperform
                  traditional betting strategies.
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 py-12 md:grid-cols-3">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-lg font-medium">
                    Data-Driven
                  </CardTitle>
                  <LineChart className="h-5 w-5 text-green-500" />
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-500">
                    We analyze millions of data points from past matches, player
                    performance, and team dynamics.
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-lg font-medium">
                    AI-Powered
                  </CardTitle>
                  <Brain className="h-5 w-5 text-green-500" />
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-500">
                    Our reinforcement learning algorithms continuously improve
                    by learning from each match outcome.
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-lg font-medium">
                    Game-Specific
                  </CardTitle>
                  <Target className="h-5 w-5 text-green-500" />
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-500">
                    We specialize exclusively in CS2, allowing us to develop
                    deep expertise in this specific esport.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32 bg-gray-100">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
                  Meet Our Team
                </h2>
                <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  A diverse group of experts in machine learning, game theory,
                  and Counter Strike 2.
                </p>
              </div>
            </div>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 py-12">
              {[
                {
                  name: 'Nathan Ho',
                  role: 'Web Developer | RL Engineer',
                  bio: 'Developed front facing client for handling schematics and model training.',
                },
                {
                  name: 'Matt Protacio',
                  role: 'Data Engineer | RL Engineer',
                  bio: 'Data and web scrapper engineer for CS2 analytics.',
                },
                {
                  name: 'Alexey Kuraev',
                  role: 'Backend Engineer | RL Engineer',
                  bio: 'Python systems expert who built our API infrastructure.',
                },
              ].map((member, index) => (
                <Card key={index} className="overflow-hidden">
                  {/* <div className="aspect-square relative"> */}
                  {/*   <img */}
                  {/*     src={`/placeholder.svg?height=300&width=300&text=${member.name}`} */}
                  {/*     alt={member.name} */}
                  {/*     className="object-cover" */}
                  {/*   /> */}
                  {/* </div> */}
                  <CardHeader>
                    <CardTitle>{member.name}</CardTitle>
                    <CardDescription>{member.role}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">{member.bio}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32">
          <div className="container px-4 md:px-6">
            <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
              <div className="space-y-4">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
                  Our Technology
                </h2>
                <p className="text-gray-500 md:text-xl/relaxed">
                  Q-BET's reinforcement learning system utilizes dynamic
                  programming algorithms, like PPO, to analyze real-time game
                  data and historical patterns to predict match outcomes with
                  exceptional accuracy.
                </p>
                <ul className="grid gap-3">
                  {[
                    'Deep neural networks trained on years of professional CS2 matches',
                    'Real-time data processing of in-game events',
                    'Player performance modeling across different maps and scenarios',
                    'Team composition and strategy analysis',
                    'Continuous learning and model improvement',
                  ].map((feature, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <Trophy className="h-5 w-5 text-green-500" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="relative h-[400px] rounded-lg overflow-hidden bg-black">
                <div className="absolute inset-0 flex items-center justify-center">
                  <Code className="h-24 w-24 text-green-500 opacity-20" />
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-black to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-6">
                  <div className="space-y-2">
                    <h3 className="text-xl font-bold text-white">
                      CS-RL Algorithm
                    </h3>
                    <p className="text-sm text-gray-300">
                      Our proprietary algorithm processes over 500 data points
                      per second during live matches.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32 bg-green-500 text-white">
          <div className="container px-4 md:px-6 text-center">
            <div className="flex flex-col items-center space-y-4">
              <Users className="h-12 w-12" />
              <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
                Questions? Contact Us!
              </h2>
              <p className="max-w-[600px] text-white/80 md:text-xl/relaxed">
                Q-BET is currently an academic study and does not endorse
                gambling. For any inquiries or collaboration, please reach out
                to us.
              </p>
              <Button className="bg-white text-green-500 hover:bg-white/90">
                Contact Form
              </Button>
            </div>
          </div>
        </section>
      </main>
      <footer className="w-full border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
          <p className="text-sm text-gray-500 md:text-base">
            © {new Date().getFullYear()} Q-BET. Open Source.
          </p>
        </div>
      </footer>
    </>
  );
};
