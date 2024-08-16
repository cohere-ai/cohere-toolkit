'use client';

import { useAgent, useAgentTasks } from '@/hooks/agents';

type Props = {
  params: {
    agentId: string;
  };
  searchParams: Record<string, string>;
};

const Page = ({ params }: Props) => {
  const agentId = params.agentId;
  const {
    data: agentTasks,
    isLoading: isTaskLoading,
    error: isTaskError,
  } = useAgentTasks({ agentId });
  const { data: agent, isLoading, error } = useAgent({ agentId });

  if (error || isTaskError) {
    return <div>Error: {error?.message}</div>;
  }

  if (isLoading || isTaskLoading) {
    return <div>Loading...</div>;
  }

  if (!agentTasks || agentTasks.length === 0) {
    return (
      <div className="m-12">
        <h1 className="mb-4 mt-4 bg-slate-800 p-16 text-2xl">Tasks report for {agent?.name} </h1>
        <h1 className="mb-4 mt-4 bg-slate-800 p-16 text-xl">No tasks yet </h1>
      </div>
    );
  }

  return (
    <div className="m-12">
      <h1 className="mb-4 mt-4 bg-slate-800 p-16 text-2xl">Tasks report for {agent?.name} </h1>
      <table className="table-fixed border-separate border-spacing-2  border border-r-4 border-slate-500 bg-slate-800 p-8">
        <thead className="text-xl">
          <tr>
            <th>Task ID</th>
            <th>Task Name</th>
            <th>Task Status</th>
            <th>Task Result</th>
            <th>Exception Snippet</th>
          </tr>
        </thead>
        <tbody className="text">
          {(agentTasks || []).map((task) => (
            <tr
              key={task.task_id}
              className={task.status === 'SUCCESS' ? 'bg-inherit' : 'bg-orange-800'}
            >
              <td>{task.task_id}</td>
              <td>{task.name}</td>
              <td>{task.status}</td>
              <td>{task?.result ? JSON.stringify(task.result, null, 2) : ''}</td>
              <td>{task?.exception_snippet || ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Page;
