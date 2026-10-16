// Type declarations for CSS modules used in web-platform components
declare module '*.module.css' {
  const classes: { readonly [key: string]: string };
  export default classes;
}
