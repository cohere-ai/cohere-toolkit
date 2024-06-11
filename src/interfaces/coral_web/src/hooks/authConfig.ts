export const useAuthConfig = () => {
  return {
    loginUrl: '/login',
    registerUrl: '/register',
    logoutUrl: '/logout',
    login: {
      googleClientId: 'googleClientId',
    },
    baseUrl: 'http://localhost:4000',
  };
};
