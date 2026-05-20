# 11_revenue_proxy.R
# Cyclistic Bike-Share Case Study — R Module
#
# Illustrative revenue model: what is the annual membership revenue upside
# if a portion of casual riders convert to annual members?
#
# Assumptions (based on publicly documented Divvy pricing):
#   - Casual riders: $1/unlock + $0.17/min (electric) or $0.16/min (classic)
#   - Annual membership: $119.88/year (Divvy data — may vary)
#   - Unique rider IDs not available — casual ride count used as proxy
#
# Introduces: tibble(), sprintf(), formatted console tables in R

library(tidyverse)

csv_folder <- file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
                        "Data", "DATAfile_Consolidated")
csv_files  <- list.files(csv_folder, pattern = "\\.csv$", full.names = TRUE)
trips      <- read_csv(csv_files, show_col_types = FALSE)

# ---------------------------------------------------------------------------
# Pricing assumptions
# ---------------------------------------------------------------------------

MEMBER_ANNUAL   <- 119.88   # annual membership fee ($)
CASUAL_RIDES    <- trips |> filter(member_casual == "casual") |> nrow()

cat("--- Revenue Proxy Model ---\n")
cat("Total casual rides used as conversion proxy:", format(CASUAL_RIDES, big.mark = ","), "\n")
cat("Assumed annual membership fee: $", MEMBER_ANNUAL, "\n\n")

# ---------------------------------------------------------------------------
# Theoretical maximum (100% conversion)
# ---------------------------------------------------------------------------

theoretical_max <- CASUAL_RIDES * MEMBER_ANNUAL
cat("Theoretical maximum (100% conversion):",
    scales::dollar(theoretical_max), "\n")
cat("Note: presented for scale only — not a realistic target.\n\n")

# ---------------------------------------------------------------------------
# Conversion sensitivity table
#
# sprintf() formats numbers into strings with precise control —
# similar to Python's f-strings but older syntax.
# scales::dollar() and scales::comma() apply currency/comma formatting.
# ---------------------------------------------------------------------------

cat("--- Conversion Sensitivity Table ---\n")
cat(sprintf("%-18s  %15s  %22s\n", "Conversion Rate", "New Members", "Annual Revenue Upside"))
cat(strrep("-", 60), "\n")

conversion_rates <- c(0.05, 0.10, 0.15, 0.20, 0.25)

sensitivity <- tibble(
  rate        = conversion_rates,
  new_members = as.integer(CASUAL_RIDES * rate),
  upside      = new_members * MEMBER_ANNUAL
)

for (i in seq_len(nrow(sensitivity))) {
  cat(sprintf("%-18s  %15s  %22s\n",
    paste0(sensitivity$rate[i] * 100, "%"),
    scales::comma(sensitivity$new_members[i]),
    scales::dollar(sensitivity$upside[i])
  ))
}

cat("\n")

# ---------------------------------------------------------------------------
# Bar chart — revenue upside by conversion rate
# ---------------------------------------------------------------------------

ggplot(sensitivity, aes(x = factor(paste0(rate * 100, "%"),
                                   levels = paste0(conversion_rates * 100, "%")), y = upside)) +
  geom_col(fill = "#2A9D8F", width = 0.6) +
  geom_text(
    aes(label = scales::dollar(upside, scale = 1e-6, suffix = "M", accuracy = 0.1)),
    vjust = -0.4,
    size  = 4
  ) +
  scale_y_continuous(
    labels = scales::dollar_format(scale = 1e-6, suffix = "M"),
    limits = c(0, max(sensitivity$upside) * 1.15)
  ) +
  labs(
    title    = "Even a 5% Conversion Rate Represents Significant Revenue",
    subtitle = paste0("Based on ", scales::comma(CASUAL_RIDES),
                      " casual rides × conversion rate × $", MEMBER_ANNUAL, "/yr membership"),
    x        = "Conversion Rate",
    y        = "Annual Revenue Upside",
    caption  = "Illustrative model only. Source: Divvy Trip Data / Divvy pricing"
  ) +
  theme_minimal(base_size = 13)

ggsave(
  file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
            "Visuals", "R", "11_revenue_proxy.png"),
  width = 8, height = 6, dpi = 150
)
