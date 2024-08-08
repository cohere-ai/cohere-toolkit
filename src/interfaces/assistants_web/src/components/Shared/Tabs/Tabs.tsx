'use client';

import { Tab, TabGroup, TabList, TabPanel, TabPanels } from '@headlessui/react';
import { ReactNode, useEffect, useRef } from 'react';

import { Skeleton, Text } from '@/components/Shared';
import { cn } from '@/utils';

type TabsProps = {
  tabs: ReactNode[];
  isLoading?: boolean;
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
  isLoading = false,
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
    <TabGroup
      as="div"
      className={tabGroupClassName}
      manual
      selectedIndex={selectedIndex}
      onChange={handleTabChange}
    >
      <div className="flex w-full items-end">
        <TabList
          className={cn(
            'flex',
            'w-full justify-between overflow-x-auto md:justify-start',
            'border-none',
            { 'md:w-fit': fitTabsContent },
            className
          )}
          ref={ref}
        >
          {tabs.map((label, i) => (
            <Tab
              key={i}
              className={cn(
                'flex w-full flex-1 flex-col focus:outline-none md:flex-initial',
                'border-coral-700 dark:border-evolved-green-700',
                {
                  'border-b-4': i === selectedIndex,
                  'border-b border-marble-950 dark:border-volcanic-150': i !== selectedIndex,
                  hidden: hiddenIndexes.includes(i),
                }
              )}
            >
              {({ selected }) => {
                // If the label is a React node, we want the node to handle their own margins.
                return (
                  <div
                    className={cn(
                      'group flex w-full items-center justify-center gap-x-3 px-6',
                      tabClassName
                    )}
                  >
                    <Text
                      as="span"
                      styleAs="label"
                      className={cn(
                        'my-3 whitespace-nowrap group-hover:text-volcanic-100 dark:group-hover:text-mushroom-950',
                        {
                          'font-medium text-volcanic-100 dark:text-mushroom-950': selected,
                          'text-volcanic-400 dark:text-volcanic-500': !selected,
                        }
                      )}
                    >
                      {label}
                    </Text>
                    {subLabels.length > 0 && subLabels[i] && (
                      <Text
                        as="span"
                        styleAs="overline"
                        className="whitespace-nowrap text-volcanic-400 dark:text-mushroom-800"
                      >
                        {subLabels[i]}
                      </Text>
                    )}
                  </div>
                );
              }}
            </Tab>
          ))}
        </TabList>
        <div className="hidden flex-1 border-b border-marble-950 md:block dark:border-volcanic-150" />
      </div>
      {children && (
        <TabPanels className={cn('w-full pt-10', panelsClassName)}>
          {children.filter(Boolean).map((child, i) => (
            <TabPanel key={i} className={tabPanelClassName}>
              {isLoading ? (
                <div className="flex flex-col gap-y-3">
                  <Skeleton className="h-6 w-full" />
                  <Skeleton className="h-6 w-full" />
                  <Skeleton className="h-6 w-full" />
                </div>
              ) : (
                child
              )}
            </TabPanel>
          ))}
        </TabPanels>
      )}
    </TabGroup>
  );
};
