import { Card, CardContent, CardTitle } from '../../ui/card';
import { MatchesTable } from './training-table';

export const TrainingTab = () => {
  return (
    <div>
      <Card className="p-5 mb-6">
        <CardTitle className="flex justify-start">Match Data</CardTitle>
        <CardContent className="flex justify-start">
          <MatchesTable />
        </CardContent>
      </Card>
      <Card className="p-5">
        <CardTitle className="flex justify-start">In-Game Data</CardTitle>
        <CardContent className="flex justify-start">
          <MatchesTable />
        </CardContent>
      </Card>
    </div>
  );
};
