// Validates email address complies with the spec at https://tools.ietf.org/html/rfc5322#section-3.4.1
// local-part "@" domain
// where local-part and domains are each 64 characters or less

export const simpleEmailValidation = (email: string) => {
  const emailRegex =
    /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  const isPotentiallyValid = emailRegex.test(email);
  if (!isPotentiallyValid) {
    return false;
  }

  const parts = email.split('@');
  if (parts.length !== 2) {
    return false;
  }
  const [before, after] = parts;
  return before.length > 0 && before.length <= 64 && after.length > 0 && after.length <= 64;
};
