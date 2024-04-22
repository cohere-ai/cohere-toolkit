import { Tab } from '@headlessui/react';
import { ReactNode, isValidElement, useEffect, useRef } from 'react';

import { Text } from '@/components/Shared';
import { cn } from '@/utils';

type TabsProps = {
  tabs: ReactNode[];
  hiddenTabs?: string[];
  subLabels?: string[];
  fitTabsContent?: boolean;
  selectedIndex?: number;
  tabGroupClassName?: string;
  tabPanelClassName?: string;
  className?: string;
  panelsClassName?: string;
  tabClassName?: string;
  children?: React.ReactNode[];
  onChange?: (index: number) => void;
};

/**
 * @description Tabs takes an array of strings as tabs and an array of React nodes as children.
 *
 * @param fitTabsContent - Used for expanding the tabs to the full width of the parent container.
 * If true, the tabs width will be set to fit their content and the remaining space will be taken
 * by a div with a border.
 * If false, the tabs will be equally distributed across the parent container.
 */
export const Tabs: React.FC<TabsProps> = ({
  tabs,
  hiddenTabs = [],
  subLabels = [],
  fitTabsContent = true,
  selectedIndex,
  className = '',
  tabGroupClassName = '',
  tabPanelClassName = '',
  panelsClassName = '',
  tabClassName = '',
  onChange,
  children,
}) => {
  const ref = useRef<HTMLDivElement>(null);

  const handleTabChange = (index: number | React.FormEvent<HTMLDivElement>) => {
    if (onChange && typeof index === 'number') onChange(index);
  };

  useEffect(() => {
    // Scroll to the selected tab if it's not visible.
    if (ref.current && ref.current.scrollTo) {
      const scrollLeft = (selectedIndex ?? 0) * 100;
      ref.current.scrollTo({ left: scrollLeft, behavior: 'smooth' });
    }
  }, [selectedIndex]);

  const hiddenIndexes = hiddenTabs.map((tab) => tabs.indexOf(tab));

  return (
    <Tab.Group
      as="div"
      className={tabGroupClassName}
      manual
      selectedIndex={selectedIndex}
      onChange={handleTabChange}
    >
      <div className="flex w-full items-end">
        <Tab.List
          className={cn(
            'flex',
            'w-full justify-between overflow-x-auto md:justify-start',
            'border-none bg-white',
            { 'md:w-fit': fitTabsContent },
            className
          )}
          ref={ref}
        >
          {tabs.map((label, i) => (
            <Tab
              key={i}
              className={cn('flex w-full flex-1 flex-col focus:outline-none md:flex-initial', {
                [`border-b-4 border-primary-500`]: i === selectedIndex,
                'border-b border-marble-400': i !== selectedIndex,
                hidden: hiddenIndexes.includes(i),
              })}
            >
              {({ selected }) => {
                // If the label is a React node, we want the node to handle their own margins.
                const isReactNodeElement = isValidElement(label);
                return (
                  <div
                    className={cn(
                      'group flex w-full items-center justify-center gap-x-3 px-10',
                      tabClassName
                    )}
                  >
                    <Text
                      as="span"
                      styleAs="label"
                      className={cn('whitespace-nowrap group-hover:text-volcanic-900', {
                        'font-medium text-volcanic-900': selected,
                        'text-volcanic-700': !selected,
                        'my-3': !isReactNodeElement,
                      })}
                    >
                      {label}
                    </Text>
                    {subLabels.length > 0 && subLabels[i] && (
                      <Text
                        as="span"
                        styleAs="overline"
                        className="whitespace-nowrap text-volcanic-700"
                      >
                        {subLabels[i]}
                      </Text>
                    )}
                  </div>
                );
              }}
            </Tab>
          ))}
        </Tab.List>
        <div className="hidden flex-1 border-b border-marble-400 md:block" />
      </div>
      {children && (
        <Tab.Panels className={cn('w-full pt-10 lg:pt-14', panelsClassName)}>
          {children.filter(Boolean).map((child, i) => (
            <Tab.Panel key={i} className={tabPanelClassName}>
              {child}
            </Tab.Panel>
          ))}
        </Tab.Panels>
      )}
    </Tab.Group>
  );
};
