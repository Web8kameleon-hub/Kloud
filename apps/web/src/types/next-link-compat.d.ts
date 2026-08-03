declare module "next/link" {
  import * as React from "react";

  export interface LinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
    href: string;
    children?: React.ReactNode;
  }

  export default function Link(props: LinkProps): React.ReactElement;
}
