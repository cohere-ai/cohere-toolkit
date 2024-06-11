import { NextApiRequest, NextApiResponse } from 'next';
import Router from 'next/router';

import {
  CohereClient,
  Fetch,
} from '@/cohere-client';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    const makeCohereClient = (authToken?: string) => {
      const apiFetch: Fetch = async (resource, config) => await fetch(resource, config);
      return new CohereClient({
        hostname: 'http://localhost:8000',
        source: 'coral',
        fetch: apiFetch,
        authToken,
      });
    };
    const cohereClient = makeCohereClient();
    const { state, error } = req.query;

    if (error) {
      console.error('Error during Google OAuth callback:', error);
      return;
    }

    if (!state) {
      console.error('No code provided in Google OAuth callback');
      return;
    }

    try {
      const response = await cohereClient.googleAuth({ state: state as string });
      Router.push('/done?token=' + response.token);
    }

    // try {
    //   const response = await axios.get(`http://localhost:8000/v1/google/auth`, {
    //     params: {
    //       state,
    //     },
    //     headers: {
    //       'Content-Type': 'application/json',
    //     },
    //   });

    //   res.status(response.status).json(response.data);
    //   Router.push('/done');
    // } catch (error) {
    //   if (axios.isAxiosError(error) && error.response) {
    //     res.status(error.response.status).json({ message: error.message, data: error.response.data });
    //   } else {
    //     res.status(500).json({ message: 'Internal server error' });
    //   }
    // }
  } else {
      res.status(405).json({ message: 'Method Not Allowed' });
  }
};
