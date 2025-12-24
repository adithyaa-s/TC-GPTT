"use client";
import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import clsx from "clsx";
import { useRef } from "react";
import { mergeRefs } from "react-merge-refs";
import { handlePressableMouseEnter } from "../../lib/helpers";
import { Button } from "../Button";
import { ChevronDownVector, DropdownVector, X } from "../Icon";
import { LoadingIndicator } from "../Indicator";
import s from "./SelectControl.module.css";
export const SelectControl = ({ ref, onPointerDown, onKeyDown, onPointerEnter, onInteract, invalid, disabled, children, className, variant = "outline", size = "md", block, opticallyAlign, pill = true, loading, onClearClick, selected = false, StartIcon, dropdownIconType = "dropdown", ...restProps }) => {
    const controlRef = useRef(null);
    const clearable = !!onClearClick;
    const showClearAction = clearable && selected && !loading && !disabled;
    const hasDropdownIcon = dropdownIconType && dropdownIconType !== "none" && !loading;
    const hasAnyTertiaryIndicator = showClearAction || loading || hasDropdownIcon;
    const isInteractive = !loading && !disabled;
    // Act like a <button> and fire the click handler on keyboard actions
    const handleKeyDown = (evt) => {
        switch (evt.key) {
            // NOTE: "Enter" does not open selects, as it may be an attempt to submit a form
            case "ArrowDown":
            case "ArrowUp":
            case " ":
                evt.stopPropagation();
                evt.preventDefault();
                if (onInteract) {
                    onInteract();
                }
                else {
                    // Otherwise, send a synthetic trigger event to Radix (presumably)
                    controlRef.current?.dispatchEvent(new PointerEvent("pointerdown", {
                        bubbles: true,
                        cancelable: true,
                        pointerType: "mouse", // mimic mouse interaction
                    }));
                }
                break;
            case "Enter":
                // NOTE: "Enter" does not open selects, as it may be an attempt to submit a form
                break;
            default:
                // Allow all other key presses through
                onKeyDown?.(evt);
        }
    };
    const handlePointerDown = (evt) => {
        // Don't trigger on right clicks
        if (evt.button === 2) {
            return;
        }
        // Prevent focus from entering the click target of the select
        // so that focus correctly moves into the menu.
        evt.stopPropagation();
        if (onInteract) {
            evt.preventDefault();
            onInteract();
        }
        else {
            // NOTE: cannot preventDefault() here, for radix
            onPointerDown?.(evt);
            // @ts-expect-error -- `onClick` can only be present if Radix is trying to spread it.
            // An example would be `<Popover>`, but we specifically open this component on `onPointerDown`.
            // Trigger the handler, assuming that `onPointerDown` is not going to be responsible for opening.
            restProps.onClick?.(evt);
        }
    };
    return (
    // Intentionally not using <button> and rebuilding the semantics
    _jsxs("span", { ref: mergeRefs([controlRef, ref]), className: clsx(s.SelectControl, className), 
        // Recreate <button> semantics
        role: "button", tabIndex: disabled ? -1 : 0, onPointerEnter: (evt) => {
            handlePressableMouseEnter(evt);
            onPointerEnter?.(evt);
        }, onPointerDown: isInteractive ? handlePointerDown : undefined, onKeyDown: isInteractive ? handleKeyDown : undefined, "data-variant": variant, "data-block": block ? "" : undefined, "data-pill": pill ? "" : undefined, "data-size": size, "data-optically-align": opticallyAlign, "aria-busy": loading ? "true" : undefined, "data-selected": selected, "data-loading": loading ? "" : undefined, "data-invalid": invalid ? "" : undefined, "data-disabled": disabled ? "" : undefined, "aria-disabled": disabled, ...restProps, 
        // Ignore onClick handler from Radix, because we use onPointerDown to mimic a native select
        onClick: undefined, children: [StartIcon && _jsx(StartIcon, { className: s.StartIcon }), _jsx("span", { className: s.TriggerText, children: children }), hasAnyTertiaryIndicator && (_jsxs("div", { className: s.IndicatorWrapper, children: [showClearAction && (_jsx(Button, { "aria-label": "Clear current value", className: s.Clear, onPointerDown: (evt) => {
                            // Prevent pointerDown on trigger from being captured
                            evt.stopPropagation();
                        }, onClick: (evt) => {
                            evt.stopPropagation();
                            evt.preventDefault();
                            onClearClick();
                        }, color: "secondary", variant: hasDropdownIcon ? "ghost" : "solid", 
                        // Mostly custom sizing through variables
                        size: "3xs", uniform: true, pill: pill, "data-only-child": !hasDropdownIcon ? "" : undefined, children: _jsx(X, {}) })), loading && _jsx(LoadingIndicator, { className: s.LoadingIndicator }), hasDropdownIcon && _jsx(DropdownIcon, { iconType: dropdownIconType })] }))] }));
};
export const DropdownIcon = ({ iconType }) => {
    return iconType === "chevronDown" ? (_jsx(ChevronDownVector, { className: clsx(s.DropdownIcon, s.DropdownIconChevron) })) : (_jsx(DropdownVector, { className: s.DropdownIcon }));
};
//# sourceMappingURL=SelectControl.js.map