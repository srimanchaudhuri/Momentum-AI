import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');

  // Create Users
  const user1 = await prisma.user.create({
    data: {
      name: 'John Doe',
      email: 'john.doe@example.com',
      password: 'hashedpassword123', // Store hashed passwords in production!
    },
  });

  const user2 = await prisma.user.create({
    data: {
      name: 'Jane Smith',
      email: 'jane.smith@example.com',
      password: 'hashedpassword456',
    },
  });

  // Create Goals
  const goal1 = await prisma.goal.create({
    data: {
      userId: user1.id,
      title: 'Lose 10kg in 3 months',
      description: 'Follow a strict diet and exercise daily.',
      startDate: new Date(),
      endDate: new Date(new Date().setMonth(new Date().getMonth() + 3)),
      status: 'ACTIVE',
    },
  });

  const goal2 = await prisma.goal.create({
    data: {
      userId: user2.id,
      title: 'Read 12 books this year',
      description: 'Read at least one book per month.',
      startDate: new Date(),
      endDate: new Date(new Date().setFullYear(new Date().getFullYear() + 1)),
      status: 'ACTIVE',
    },
  });

  // Create Progress Logs
  await prisma.progressLogs.createMany({
    data: [
      {
        userId: user1.id,
        goalId: goal1.id,
        logText: 'Did a 30-minute workout today!',
        score: 8,
      },
      {
        userId: user2.id,
        goalId: goal2.id,
        logText: 'Finished reading "Atomic Habits".',
        score: 10,
      },
    ],
  });

  // Create AI Tips
  await prisma.aITips.createMany({
    data: [
      {
        userId: user1.id,
        goalId: goal1.id,
        tipText: 'Try intermittent fasting for better fat loss.',
        recommendation: 'HIGH',
      },
      {
        userId: user2.id,
        goalId: goal2.id,
        tipText: 'Try audiobooks for a faster reading experience.',
        recommendation: 'MODERATE',
      },
    ],
  });

  console.log('✅ Seeding completed!');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
