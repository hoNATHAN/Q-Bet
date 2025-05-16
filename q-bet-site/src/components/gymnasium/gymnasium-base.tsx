import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TrainingTab } from './training-tab';
import { MatchHistoryTab } from './match-history-tab';
import { RunMatchTab } from './run-match-tab';

const tabValues = [
  {
    value: 'run-match',
    title: 'Run Match',
    content: <RunMatchTab />,
  },
  {
    value: 'match-history',
    title: 'Match History',
    content: <MatchHistoryTab />,
  },
  {
    value: 'training',
    title: 'Training',
    content: <TrainingTab />,
  },
];

const defaultTab = 'run-match';

export const GymnasiumBase = () => {
  return (
    <div className="container mx-auto py-10">
      <h1 className="flex justify-start font-bold mb-6 text-3xl">
        Gymnasium Dashboard
      </h1>

      <Tabs className="w-full" defaultValue={defaultTab}>
        <TabsList className="flex justify-start">
          {tabValues.map((t) => (
            <TabsTrigger value={t.value}>{t.title}</TabsTrigger>
          ))}
        </TabsList>
        {tabValues.map((t) => (
          <TabsContent value={t.value}>{t.content}</TabsContent>
        ))}
      </Tabs>
    </div>
  );
};
