export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  level: string;
  keySkillsCount: number;
  postedDays: number;
}

export const mockJobPool: Job[] = [
  {
    id: '1',
    title: 'Senior Account Manager',
    company: 'Salesforce',
    location: 'San Francisco, CA',
    level: 'Senior',
    keySkillsCount: 12,
    postedDays: 3,
  },
  {
    id: '2',
    title: 'Enterprise Customer Success Manager',
    company: 'HubSpot',
    location: 'Boston, MA',
    level: 'Senior',
    keySkillsCount: 10,
    postedDays: 5,
  },
  {
    id: '3',
    title: 'Strategic Account Executive',
    company: 'Stripe',
    location: 'Remote',
    level: 'Senior',
    keySkillsCount: 11,
    postedDays: 2,
  },
  {
    id: '4',
    title: 'Customer Success Lead',
    company: 'Notion',
    location: 'New York, NY',
    level: 'Senior',
    keySkillsCount: 9,
    postedDays: 7,
  },
  {
    id: '5',
    title: 'Account Management Director',
    company: 'Figma',
    location: 'San Francisco, CA',
    level: 'Senior',
    keySkillsCount: 13,
    postedDays: 4,
  },
];
