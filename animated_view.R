invisible(lapply(c('dplyr', 'data.table', 'ggplot2', 'plotly'), library, character.only = T))
for (x in c('event', 'x_hist', 'y_hist', 'col_hist', 'xy_max')){
  assign(x, fread(paste0(x, '.csv'), stringsAsFactors = F))
}

# Repeat event coordinates the number of steps
event <- 
  event %>% 
  slice(rep(1:n(), each = nrow(x_hist))) %>% 
  mutate(steps  = seq(nrow(x_hist)),
         bot  = 'event',
         colr = 2) %>% 
  select('steps', 'bot', 'x', 'y', 'colr')

# Pivot longer
x_hist[, steps := seq(nrow(x_hist))]
x_vars <- colnames(x_hist)[colnames(x_hist) != "steps"]
x_hist <- melt(x_hist, 
               measure.vars = x_vars, 
               value.name = 'x', 
               id.vars = c('steps'), 
               variable.name = 'bot',
               variable.factor = F)

y_hist[, steps := seq(nrow(y_hist))]
y_vars <- colnames(y_hist)[colnames(y_hist) != "steps"]
y_hist <- melt(y_hist, 
               measure.vars = y_vars, 
               value.name = 'y', 
               id.vars = c('steps'), 
               variable.name = 'bot',
               variable.factor = F)

col_hist[, steps := seq(nrow(col_hist))]
col_vars <- colnames(col_hist)[colnames(col_hist) != "steps"]
col_hist <- melt(col_hist, 
                 measure.vars = col_vars, 
                 value.name = 'colr', 
                 id.vars = c('steps'), 
                 variable.name = 'bot',
                 variable.factor = F)

res_dt <- merge(x_hist, y_hist, by = c('steps', 'bot'), all = T)
res_dt <- merge(res_dt, col_hist, by = c('steps', 'bot'), all = T)
res_dt <- rbind(res_dt, event)
setorder(res_dt, bot, steps)

res_dt$event_type <- ifelse(grepl('bot', res_dt$bot), 'calling', 'event')
res_dt$event_type[res_dt$colr == 1] <- 'not calling'
res_dt$size <- 3
res_dt$size[res_dt$event_type == 'event'] <- 3


base <- res_dt %>% 
  plot_ly(x = ~x, y = ~y, size = ~size) %>% 
  layout(
    title = 'Bystander Effect Simulation',
    xaxis = list(title = '', range = c(-1, xy_max$x + 1), zerolinecolor = '#efeff0',
                 gridcolor = 'ffff', showticklabels = F, gridwidth = 1,
                 showgrid = F),
    yaxis = list(title = '', range = c(-1, xy_max$y + 1), zerolinecolor = '#efeff0',
                 gridcolor = 'ffff', showticklabels = F, gridwidth = 1,
                 showgrid = F),
    plot_bgcolor = '#efeff0'
  )
base %>% 
  add_markers(color = ~event_type, frame = ~steps, ids = ~bot, colors = c('#273c75', '#c23616', '#0097e6')) %>% 
  animation_opts(200, easing = "elastic", redraw = F)
