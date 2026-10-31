from ._base import ORIGIN_CENTER, BaseAnimation, Keyframe, Layer, Origin, Pose


def _origin_css(origin: Origin) -> str:
    return f"transform-origin: {origin[0] * 100:g}% {origin[1] * 100:g}%;"


def _pose_css(pose: Pose, *, with_blur: bool, with_origin: bool) -> str:
    scale_x = pose.scale * pose.scale_x
    scale_y = pose.scale * pose.scale_y
    parts = [
        f"opacity: {pose.opacity:g};",
        f"transform: translate({pose.x:g}px, {pose.y:g}px) "
        f"rotate({pose.rotate:g}deg) scale({scale_x:g}, {scale_y:g});",
    ]
    if with_blur:
        parts.append(f"filter: blur({pose.blur:g}px);")
    if with_origin:
        parts.append(_origin_css(pose.origin))
    return " ".join(parts)


def _percent(fraction: float) -> str:
    return f"{fraction * 100:.6f}".rstrip("0").rstrip(".")


def _keyframe_css(keyframe: Keyframe, *, with_blur: bool,
                  with_origin: bool) -> str:
    pose = _pose_css(
        keyframe.pose, with_blur=with_blur, with_origin=with_origin)
    timing = (f" animation-timing-function: {keyframe.easing.css()};"
              if keyframe.easing else "")
    return f"{_percent(keyframe.at)}% {{ {pose}{timing} }}"


def _keyframes_css(layer: Layer) -> str:
    poses = [keyframe.pose for keyframe in layer.keyframes]
    with_blur = any(pose.blur > 0 for pose in poses)
    with_origin = any(pose.origin != ORIGIN_CENTER for pose in poses)
    steps = " ".join(
        _keyframe_css(keyframe, with_blur=with_blur, with_origin=with_origin)
        for keyframe in layer.keyframes
    )
    return f"@keyframes {layer.name} {{\n{steps}\n}}"


def _animation_value(layer: Layer) -> str:
    count = "infinite" if layer.iterations is None else layer.iterations
    return (f"{layer.name} {layer.duration:g}s {layer.easing.css()} "
            f"{layer.delay:g}s {count} {layer.fill}")


def build_animation_css(animation: BaseAnimation) -> str:
    layers = animation.layers()
    if not layers:
        return ""

    name = animation.css_name
    keyframes = "\n".join(_keyframes_css(layer) for layer in layers)
    value = ", ".join(_animation_value(layer) for layer in layers)

    return f"""
{keyframes}
.{name} {{
  animation: {value};
  transform-box: fill-box;
  transform-origin: center;
}}
@media (prefers-reduced-motion: reduce) {{
  .{name} {{ animation: none; }}
}}
"""
