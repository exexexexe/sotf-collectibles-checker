using TheForest.Utils;
using UnityEngine;
using UnityEngine.InputSystem;

namespace CollectiblesTracker;

// The F7 panel: every achievement's count on the left, the selected one's missing items on the right.
// Drawn with IMGUI on a 1080p virtual canvas that scales with the screen.
internal static class Panel
{
    private const float VirtualHeight = 1080f;
    private const float Line = 22f;
    private const float Pad = 14f;
    private const float LeftWidth = 330f;
    private const float ColumnWidth = 470f;
    private const int MaxColumns = 2;

    private static readonly Color Bg = new(0.07f, 0.09f, 0.08f, 0.86f);
    private static readonly Color Gold = new(0.85f, 0.65f, 0.28f);
    private static readonly Color Done = new(0.49f, 0.76f, 0.58f);
    private static readonly Color Missing = new(0.93f, 0.54f, 0.45f);
    private static readonly Color Muted = new(0.62f, 0.68f, 0.65f);
    private static readonly Color Ink = new(0.92f, 0.94f, 0.92f);

    private static int _selected;
    private static GUIStyle _text, _title, _small;

    public static bool Visible { get; set; }

    public static void HandleInput()
    {
        var keyboard = Keyboard.current;
        if (keyboard == null)
            return;
        if (keyboard[Config.ParseKey(Config.PanelKey, Key.F7)].wasPressedThisFrame)
            Visible = !Visible;
        if (keyboard[Config.ParseKey(Config.MarkersKey, Key.F8)].wasPressedThisFrame)
            MapMarkers.ToggleVisible();
        if (!Visible)
            return;
        var n = Data.Categories.Length;
        if (keyboard.pageDownKey.wasPressedThisFrame)
            _selected = (_selected + 1) % n;
        if (keyboard.pageUpKey.wasPressedThisFrame)
            _selected = (_selected + n - 1) % n;
    }

    public static void OnGUI()
    {
        if (!Visible || !Progress.Ready)
            return;
        try
        {
            Draw();
        }
        catch (Exception e)
        {
            Visible = false;
            RedLoader.RLog.Error($"Panel failed to draw: {e}");
        }
    }

    private static void Draw()
    {
        EnsureStyles();
        var scale = Screen.height / VirtualHeight;
        GUI.matrix = Matrix4x4.Scale(new Vector3(scale, scale, 1f));
        var player = LocalPlayer.Transform != null ? LocalPlayer.Transform.position : Vector3.zero;

        // Left: one row per achievement
        var rows = Data.Categories.Length;
        var leftHeight = Pad * 2 + Line * (rows + 5.5f);
        var x = 24f;
        var y = 24f;
        Box(new Rect(x, y, LeftWidth, leftHeight));
        var cy = y + Pad;
        Label(x + Pad, cy, LeftWidth, "Collectibles", _title, Gold);
        cy += Line * 1.4f;
        Label(x + Pad, cy, LeftWidth, $"{Config.PanelKey.Value} close · PgUp/PgDn switch · {Config.MarkersKey.Value} GPS markers", _small, Muted);
        cy += Line * 1.3f;
        for (var c = 0; c < rows; c++)
        {
            var cat = Data.Categories[c];
            var got = Progress.Count(c);
            var total = cat.Items.Length;
            var sel = c == _selected;
            var color = got == total ? Done : sel ? Ink : Muted;
            Label(x + Pad, cy, LeftWidth, (sel ? "> " : "   ") + cat.Title, _text, color);
            Label(x + LeftWidth - Pad - 70f, cy, 70f, $"{got}/{total}", _text, got == total ? Done : color);
            cy += Line;
        }
        cy += Line * 0.6f;
        var nearest = Nearest(player);
        Label(x + Pad, cy, LeftWidth - Pad * 2, "Nearest missing", _small, Muted);
        cy += Line * 0.9f;
        Label(x + Pad, cy, LeftWidth - Pad * 2,
            nearest is { } n ? $"{n.item.Label}, {Distance(player, n.loc)}" : "Nothing with a fixed spot left", _text, Ink);
        cy += Line;
        if (nearest is { } nn)
            Label(x + Pad, cy, LeftWidth - Pad * 2, nn.loc.Place, _small, Muted);

        DrawMissing(x + LeftWidth + 12f, y, player);
    }

    private static void DrawMissing(float x, float y, Vector3 player)
    {
        var cat = Data.Categories[_selected];
        var lines = new List<(string text, GUIStyle style, Color color)>();
        string group = null;
        for (var i = 0; i < cat.Items.Length; i++)
        {
            if (Progress.Has(_selected, i))
                continue;
            var item = cat.Items[i];
            if (item.Group != group && cat.Items.Select(it => it.Group).Distinct().Count() > 1)
            {
                group = item.Group;
                lines.Add((group.ToUpperInvariant(), _small, Muted));
            }
            group = item.Group;
            var where = item.Locs.Length > 0
                ? $"{item.Locs[0].Place}, {Distance(player, Closest(item, player))}"
                : item.Where;
            lines.Add(($"{item.Label}  <color=#9aa59f>{where}</color>", _text, Ink));
        }

        var got = Progress.Count(_selected);
        var maxRows = (int)((VirtualHeight - y - 60f - Pad * 2 - Line * 2) / Line);
        var columns = Math.Max(1, Math.Min(MaxColumns, (lines.Count + maxRows - 1) / Math.Max(1, maxRows)));
        var shownRows = Math.Min(lines.Count, maxRows * columns);
        var rowsPerColumn = Math.Max(1, (shownRows + columns - 1) / columns);
        var width = ColumnWidth * columns;
        var height = Pad * 2 + Line * (2 + Math.Max(1, rowsPerColumn) + (lines.Count > shownRows ? 1 : 0));
        Box(new Rect(x, y, width, height));

        var cy = y + Pad;
        Label(x + Pad, cy, width, $"{cat.Title}  <color=#9aa59f>{cat.Achievement} · {got}/{cat.Items.Length}</color>", _title, Gold);
        cy += Line * 1.5f;
        if (lines.Count == 0)
        {
            Label(x + Pad, cy, width, "All found.", _text, Done);
            return;
        }
        for (var i = 0; i < shownRows; i++)
        {
            var col = i / rowsPerColumn;
            var row = i % rowsPerColumn;
            var (text, style, color) = lines[i];
            Label(x + Pad + col * ColumnWidth, cy + row * Line, ColumnWidth - Pad, text, style, color);
        }
        if (lines.Count > shownRows)
            Label(x + Pad, cy + rowsPerColumn * Line, width, $"…and {lines.Count - shownRows} more", _small, Muted);
    }

    private static (Item item, Loc loc)? Nearest(Vector3 player)
    {
        (Item, Loc)? best = null;
        var bestDist = float.MaxValue;
        for (var c = 0; c < Data.Categories.Length; c++)
        {
            var cat = Data.Categories[c];
            for (var i = 0; i < cat.Items.Length; i++)
            {
                if (Progress.Has(c, i))
                    continue;
                foreach (var loc in cat.Items[i].Locs)
                {
                    var d = Flat(player, loc);
                    if (d < bestDist)
                    {
                        bestDist = d;
                        best = (cat.Items[i], loc);
                    }
                }
            }
        }
        return best;
    }

    private static Loc Closest(Item item, Vector3 player) => item.Locs.OrderBy(l => Flat(player, l)).First();

    private static float Flat(Vector3 player, Loc loc) => new Vector2(loc.X - player.x, loc.Z - player.z).magnitude;

    private static string Distance(Vector3 player, Loc loc)
    {
        var d = Flat(player, loc);
        if (d < 25f)
            return "right here";
        var deg = Mathf.Atan2(loc.X - player.x, loc.Z - player.z) * Mathf.Rad2Deg;
        var dir = new[] { "N", "NE", "E", "SE", "S", "SW", "W", "NW" }[(int)Mathf.Repeat(Mathf.Round(deg / 45f), 8f)];
        var dist = d >= 1000f ? $"{d / 1000f:0.0} km" : $"{Mathf.Round(d / 10f) * 10f:0} m";
        return $"{dist} {dir}";
    }

    private static void Box(Rect r)
    {
        var old = GUI.color;
        GUI.color = Bg;
        GUI.DrawTexture(r, Texture2D.whiteTexture);
        GUI.color = old;
    }

    private static void Label(float x, float y, float w, string text, GUIStyle style, Color color)
    {
        style.normal.textColor = color;
        GUI.Label(new Rect(x, y, w, Line + 4f), text, style);
    }

    private static void EnsureStyles()
    {
        if (_text != null)
            return;
        _text = new GUIStyle(GUI.skin.label) { fontSize = 16, richText = true, wordWrap = false, clipping = TextClipping.Clip };
        _title = new GUIStyle(_text) { fontSize = 19, fontStyle = FontStyle.Bold };
        _small = new GUIStyle(_text) { fontSize = 13 };
    }
}
